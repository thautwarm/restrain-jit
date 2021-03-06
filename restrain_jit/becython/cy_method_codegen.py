from restrain_jit.becython.phi_vm import *
from restrain_jit.becython.cy_jit_common import *
from restrain_jit.becython.cy_jit_ext_template import mk_call_record, mk_call_record_t
from restrain_jit.abs_compiler.py_apis import NS
from restrain_jit.jit_info import PyCodeInfo, PyFuncInfo
from restrain_jit.vm.am import ValSymbol, Symbol
from restrain_jit.utils import CodeOut, MissingDict
from collections import OrderedDict
from contextlib import contextmanager
from functools import singledispatch
from string import Template
import typing as t

try:
    from .cy_jit import JITSystem, JITFunctionHoldPlace
except ImportError:
    pass


class UndefGlobal:
    pass


preludes = [
    "cimport restrain_jit.becython.cython_rts.RestrainJIT as RestrainJIT",
    "from restrain_jit.becython.cython_rts.RestrainJIT cimport Cell",
    "from libc.stdint cimport int64_t, int8_t",
    "from libcpp.cast cimport reinterpret_cast",
    "from restrain_jit.becython.cython_rts.hotspot cimport typeid, inttoptr, pytoint",
]

base_call_prelude = """
from libcpp.vector cimport vector as std_vector
ctypedef $call_record_t call_record_t
ctypedef std_vector[call_record_t] call_records_t

cdef class NonJITCallRecorder:
    cdef call_records_t records
    cdef int64_t bound

    def __init__(self):
        self.bound = 233
        self.records = call_records_t()

    cdef record(self, call_record_t m):
        self.records.push_back(m)

    cdef int8_t check_bounded(self):
        return self.records.size() % self.bound == 0

    def load_type(self, int64_t i):
        return <object>(inttoptr(i))

    def get(self):
        return self.records

cdef NonJITCallRecorder {0}    
cdef object {1}

def {2}(a, b):
    global {0}, {1}
    {0} = a
    {1} = b
""".format(recorder, notifier, method_init_recorder_and_notifier)


class CodeEmit:

    def __init__(self, jit_system: 'JITSystem', code_info: PyCodeInfo,
                 function_place: 'JITFunctionHoldPlace'):
        self.priority = Import
        self.other_fptrs = {}
        self.prefixes = [""]
        self.gen_sym_id = 0
        self.function_place = function_place
        self.jit_system = jit_system

        def emit_line(line):
            code_out[self.priority].append(line)

        def persistent_code():
            nonlocal code_out
            code_out = persistent_code_out

        self.persistent_code = persistent_code

        def base_method_code():
            nonlocal code_out
            code_out = once_code_out

        self.base_method_code = base_method_code

        self.emit_line = emit_line

        # Name generator
        mangle_map = self.mangle_map = MissingDict(lambda: "{}{}".format(
            mangle_head, len(mangle_map)))

        self.symbol_map = symbom_map = MissingDict(lambda: "{}{}".format(
            sym_head, len(symbom_map)))

        self.fn_map = fn_map = MissingDict(lambda: "{}{}".format(fn_head, len(fn_map)))

        # End name generator
        code_out = persistent_code_out = CodeOut()
        for each in preludes:
            self += each

        glob_deps = code_info.glob_deps

        # TODO: some globals, like 'type' or others, don't need to initialize here.
        # Also, the initialization of those can badly hurt the performance, e.g., 'type'.

        def is_supported_builtin(s):
            if s in ('type', 'range', 'len', 'print'):
                return False
            raise NameError(s)

        actual_glob = function_place.globals
        self.glob = {
            each: self.gensym(each)
            for each in glob_deps
            if each in actual_glob or is_supported_builtin(each)
        }

        function_place.glob_deps = tuple(self.glob.keys())
        fn_name = self.mangle(code_info.name)

        once_code_out = CodeOut()
        code_out = once_code_out
        self.priority = TypeDecl
        self += Template(base_call_prelude).substitute(
            call_record_t=mk_call_record_t(code_info.argcount))

        # BASE_METHOD_CODE
        #  different methods of a JIT function
        #  varies from their behaviours/codegen rules of following block
        code_out = once_code_out
        self.priority = Customizable
        cellvars = code_info.cellvars
        arguments = OrderedDict((e, self.mangle(e) if e not in cellvars else self.gensym(e))
                                for e in code_info.freevars + code_info.argnames)
        function_place.method_arguments = tuple(arguments.values())
        self += 'cdef {}({}):'.format(fn_name, ', '.join(arguments.values()))

        code_out = once_code_out
        self.priority = Customizable
        with indent(self):
            if code_info.argcount:
                typeids = mk_call_record(list(arguments.values()))
                self += "{}# BEGIN MONITOR".format(self.prefix)
                self += "{}cdef call_record_t res_call_record = {}".format(
                    self.prefix, typeids)
                self += "{}{}.record(res_call_record)".format(self.prefix, recorder)
                self += "{}if {}.check_bounded(): {}()".format(self.prefix, recorder,
                                                               notifier)
                self += "{}# END MONITOR".format(self.prefix)

        # PERSISTENT CODE
            code_out = persistent_code_out
            self.priority = Normal
            cellvars = code_info.cellvars
            for cell in cellvars:
                actual_cell = self.mangle(cell)
                if cell in code_info.argnames:
                    cell_in_arg = self.gensym(cell)
                    self += "{}cdef Cell {} = {}.Cell({})".format(
                        self.prefix, actual_cell, NS.RestrainJIT, cell_in_arg)
                else:
                    self += "{}cdef Cell {} = {}.Cell(None)".format(
                        self.prefix, actual_cell, NS.RestrainJIT)

        code_out = persistent_code_out
        self.priority = Normal

        with indent(self):
            self.emit_instrs(code_info.instrs)

        self.declare_globals()
        jit_system.remember_partial_code(function_place, code_out=persistent_code_out)
        # dict.update not work here.
        once_code_out.merge_update(persistent_code_out)
        base_call_code = '\n'.join(once_code_out.to_code_lines())
        function_place.fn_ptr_name = fn_name
        jit_system.generate_base_method(function_place, code=base_call_code)

    @property
    def prefix(self):
        return self.prefixes[-1]

    def gensym(self, s: str = ""):
        if not s:
            base = 'r3e'
        elif s.isidentifier():
            base = s
        else:
            base = ''.join(e for e in s if e.isidentifier())
        ret = "{}{}_{}".format(gensym_head, self.gen_sym_id, base)
        self.gen_sym_id += 1
        return ret

    def indent(self):
        self.prefixes.append(self.prefix + IDENTATION_SECTION)

    def dedent(self):
        self.prefixes.pop()

    def mangle(self, n: str):
        if n.isidentifier():
            return var_head + n
        return self.mangle_map[n]

    def declare_globals(self):
        """
        strongly-typed globals?
        """
        p = self.priority
        self.priority = Finally

        prefix = "    "

        arguments_comma_lst = ', '.join(self.glob.keys())

        global_vars_comma_lst = ', '.join(self.glob.values())
        fptrs_comma_lst = ', '.join(self.other_fptrs.keys())

        # use as 'module_init_globals(**global_dict)'
        self += "cpdef method_init_globals({}):".format(arguments_comma_lst)
        self += '{}global {}'.format(prefix, global_vars_comma_lst)

        jit_fptr_index = self.gensym('ptr_index')
        # use as 'method_init_fptrs(jit_system.jit_fptr_index)'
        self += "cpdef method_init_fptrs({}):".format(jit_fptr_index)
        self += '{}global {}'.format(prefix, fptrs_comma_lst)

        for k, v in self.other_fptrs.items():
            self += "{}{} = {}[{}]".format(prefix, k, jit_fptr_index, v)

        for k, v in self.glob.items():
            self += '{}{} = {}'.format(prefix, k, v)

        self.priority = TypeDecl
        for var in self.glob.values():
            self += "cdef object {}".format(var)

        for var in self.other_fptrs.keys():
            self += "cdef object {}".format(var)

        self.priority = p

    def declare_symbol(self, s: str):
        if s in self.symbol_map:
            return self.symbol_map[s]
        n = self.symbol_map[s]
        p = self.priority
        self.priority = TypeDecl
        try:
            self += "cdef int64_t {} = {}.get_symbol({!r})".format(n, NS.RestrainJIT, s)
        finally:
            self.priority = p
        return n

    def __iadd__(self, other):
        self.emit_line(other)
        return self

    def set_cont(self, label_i):
        self += "{}{} = {}".format(self.prefix, cont_name, label_i)

    def set_last_cont(self, last=None):
        self += "{}{} = {}".format(self.prefix, last_cont_name, last or cont_name)

    def emit_instrs(self, instrs: t.List[Instr]):

        tmplt = "{}cdef int {} = 0"
        self += tmplt.format(self.prefix, last_cont_name)
        self += tmplt.format(self.prefix, cont_name)
        self += tmplt.format(self.prefix, lineno_name)
        self += "{}# Control flow graph splitted".format(self.prefix)
        self += "{}while True:".format(self.prefix)
        with indent(self):
            for each in instrs:
                emit(each, self)


@singledispatch
def emit(a: Instr, self: CodeEmit):
    raise NotImplementedError(a)


def emit_const(self: CodeEmit, r: object):
    if isinstance(r, (ValSymbol, Symbol)):
        return r.s
        # var_name = self.declare_symbol(r.s)
        # return var_name
    elif isinstance(r, PyCodeInfo):
        fn_place = self.jit_system.allocate_place_for_function(r)
        fn_place.globals_from(self.function_place.globals)
        CodeEmit(self.jit_system, r, fn_place)
        n = self.gensym(fn_place.name_that_makes_sense)
        self.other_fptrs[n] = fn_place.unique_index
        return n
    return repr(r)


def emit_repr(self: CodeEmit, r: Repr) -> str:
    if isinstance(r, Const):
        return emit_const(self, r.val)
    elif isinstance(r, Reg):
        return self.mangle(r.n)
    elif isinstance(r, Prim):
        if not r.qual:
            # python const
            name = r.n
            glob_name = self.glob.get(name, name)
            return glob_name
        return "{}.{}".format(r.qual, r.n)
    else:
        raise TypeError(r)


@contextmanager
def indent(self: CodeEmit):
    self.indent()
    try:
        yield
    finally:
        self.dedent()


@emit.register
def set_lineno(n: SetLineno, self: CodeEmit):
    self += "{}{} = {}".format(self.prefix, lineno_name, n.lineno)


def phi_for_given_branch(self, var_dict):
    for k, r in var_dict.items():
        v = emit_repr(self, r)
        k = self.mangle(k)
        self += "{}{} = {}".format(self.prefix, k, v)


def phi(self: CodeEmit, phi_dict):

    def app(_self, _token, _var_dict):
        _self += "{}{}:".format(_self.prefix, _token)
        with indent(_self):
            phi_for_given_branch(_self, _var_dict)

    head, *init, end = phi_dict.items()

    token = "if {} == {}".format(head[0], last_cont_name)
    app(self, token, head[1])

    for come_from, var_dict in init:
        token = "elif {} == {}".format(come_from, last_cont_name)
        app(self, token, var_dict)

    self += "# must from label {}".format(head[0])
    app(self, "else", end[1])


@emit.register
def label(n: BeginBlock, self: CodeEmit):
    self += "{}if {} == {}:".format(self.prefix, n.label, cont_name)

    self.indent()
    self.set_cont(n.label)
    phi_dict = n.phi
    if phi_dict:
        self += "{}# Phi".format(self.prefix)
        if len(phi_dict) is 1:
            l, var_dict = next(iter(phi_dict.items()))
            self += "# must from label {}".format(l)
            phi_for_given_branch(self, var_dict)
        else:
            phi(self, phi_dict)


@emit.register
def end(_: EndBlock, self: CodeEmit):
    self.set_last_cont(cont_name)
    self.set_cont('{} + 1'.format(cont_name))
    self += "{}continue".format(self.prefix)
    self.dedent()


@emit.register
def ret(r: Return, self: CodeEmit):
    self += "{}return {}".format(self.prefix, emit_repr(self, r.val))


@emit.register
def set_cont(c: Jmp, self: CodeEmit):
    prefix = self.prefix
    self.set_last_cont()
    self.set_cont(c.label)
    self += "{}continue".format(prefix)


@emit.register
def set_conf_if(c: JmpIf, self: CodeEmit):
    self += "{}if {}:".format(self.prefix, emit_repr(self, c.cond))
    with indent(self):
        prefix = self.prefix
        self += "{}{} = {}".format(prefix, cont_name, c.label)
        self.set_last_cont()
        self += "{}continue".format(prefix)


@emit.register
def store(st: Store, self: CodeEmit):
    ptr_tag = self.mangle(st.target)
    val = emit_repr(self, st.val)
    self += "{}{}.setref_cell({}) = {}".format(self.prefix, NS.RestrainJIT, ptr_tag, val)


@emit.register
def load(l: Load, self: CodeEmit):
    tag = self.mangle(l.target)
    ptr = emit_repr(self, l.reg)
    self += "{}{} = {}.deref_cell({})".format(self.prefix, tag, NS.RestrainJIT, ptr)


@emit.register
def ass(a: Ass, self: CodeEmit):
    tag = self.mangle(a.target)
    val = emit_repr(self, a.val)
    self += "{}{} = {}".format(self.prefix, tag, val)


@emit.register
def app(a: App, self: CodeEmit):
    tag = ""
    if a.target:
        tag = "{} = ".format(self.mangle(a.target))
    args = list(map(lambda x: emit_repr(self, x), a.args))
    if isinstance(a.f, Prim) and a.f.qual == NS.RestrainJIT:
        if a.f.n == "py_subscr":
            assert len(args) is 2
            self += "{}{}({}[{}])".format(self.prefix, tag, args[0], args[1])
            return
        if a.f.n == "py_get_attr":
            assert len(args) is 2
            self += "{}{}{}.{}".format(self.prefix, tag, args[0], args[1])
            return
        if a.f.n == "py_store_attr":
            assert len(args) is 3
            self += "{}{}.{} = {}".format(self.prefix, args[0], args[1], args[2])
            return
        op = {
            'py_add': '+',
            'py_sub': '-',
            'py_mul': '*',
            'py_truediv': '/',
            'py_floordiv': '//',
            'py_mod': '%',
            'py_lsh': '<<',
            'py_rsh': '>>',
            'py_xor': '^',
            'py_or': '|',
            'py_and': '&',
            'py_pow': '**',
            'py_is': 'is',
            'py_gt': '>',
            'py_lt': '<',
            'py_in': 'in',
            'py_not_in': 'not in',
            'py_ge': '>=',
            'py_le': '<=',
            'py_neq': '!=',
            'py_eq': '==',
        }.get(a.f.n, None)

        if op is not None:
            assert len(args) is 2
            self += "{}{}({} {} {})".format(self.prefix, tag, args[0], op, args[1])
            return
        op = {
            "py_is_none": '{} is None',
            'py_is_true': '{} is True',
            'py_not': 'not {}',
            'py_inv': '~{}',
            'py_neg': '-{}',
        }.get(a.f.n, None)
        if op is not None:
            assert len(args) is 1
            self += "{}{}({})".format(self.prefix, tag, op.format(args[0]))
            return
    f = emit_repr(self, a.f)
    self += "{}{}{}({})".format(self.prefix, tag, f, ', '.join(args))
