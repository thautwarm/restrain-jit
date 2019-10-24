from restrain_jit.becython.phi_vm import *
from restrain_jit.abs_compiler.py_apis import NS
from restrain_jit.jit_info import PyCodeInfo, PyFuncInfo
from restrain_jit.vm.am import ValSymbol, Symbol
from dataclasses import dataclass
from enum import Enum, auto
from io import StringIO
from collections import OrderedDict
from contextlib import contextmanager
from functools import singledispatch
import typing as t


class CodeGenOptions:
    # FIXME
    pass


class MissingDict(dict):

    def __init__(self, fact):
        dict.__init__(self)
        self.fact = fact

    def __missing__(self, key):
        val = self[key] = self.fact()
        return val


class CodeOut(OrderedDict):

    def __missing__(self, key):
        v = self[key] = []
        return v


class CodeEmitter:
    lineno_name = "restrain_lineno"
    cont_name = "res_cont"
    last_cont_name = "res_last_cont"
    mangle_head = 'res_mg_'
    gensym_head = "res_gen_"
    var_head = 'res_var_'
    sym_head = "symbol_"
    glob_head = "global_"
    fn_head = "localfn_"

    def __init__(self, code_out: t.Dict[int, t.List[str]],
                 global_name_mapping: dict):
        self.prefixes = [""]
        self.glob = global_name_mapping
        self.priority = 0
        self.gen_sym_id = 0
        mangle_head = self.mangle_head
        sym_head = self.sym_head
        fn_head = self.fn_head

        mangle_map = self.mangle_map = MissingDict(
            lambda: "{}{}".format(mangle_head, len(mangle_map)))

        self.symbol_map = symbom_map = MissingDict(
            lambda: "{}{}".format(sym_head, len(symbom_map)))

        self.fn_map = fn_map = MissingDict(lambda: "{}{}".format(
            fn_head, len(fn_map)))

        def emit_line(line):
            code_out[self.priority].append(line)

        self.emit_line = emit_line

    @classmethod
    def declare_func_info(self, fn_info: PyFuncInfo, ):
        code_out = CodeOut()
        glob_deps = fn_info.r_codeinfo.glob_deps
        glob = {}
        ce = CodeEmitter(code_out, glob)
        ce.glob.update({each: ce.gensym(each) for each in glob_deps})
        name = ce.emit_codeinfo(fn_info.r_codeinfo)
        return name, code_out

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
        ret = "{}{}_{}".format(self.gensym_head, self.gen_sym_id, base)
        self.gen_sym_id += 1
        return ret

    def indent(self):
        self.prefixes.append(self.prefix + "    ")

    def dedent(self):
        self.prefixes.pop()

    def mangle(self, n: str):
        if n.isidentifier():
            return self.var_head + n
        return self.mangle_map[n]

    def declare_symbol(self, s: str):
        if s in self.symbol_map:
            return self.symbol_map[s]
        n = self.symbol_map[s]
        p = self.priority
        self.priority = -2
        try:
            self += "cdef int64_t {} = {}.get_symbol({!r})".format(
                n, NS.RestrainJIT, s)
        finally:
            self.priority = p
        return n

    def declare_fptr(self, code: PyCodeInfo):
        if id(code) in self.fn_map:
            return self.fn_map[id(code)]
        p = self.priority
        self.priority = -1
        try:
            n = self.emit_codeinfo(code)
            self.fn_map[id(code)] = n
        finally:
            self.priority = p
        return

    def __iadd__(self, other):
        self.emit_line(other)
        return self

    def set_cont(self, label_i):
        self += "{}{} = {}".format(self.prefix, self.last_cont_name,
                                   label_i)

    def set_last_cont(self, last=None):
        self += "{}{} = {}".format(self.prefix, self.last_cont_name,
                                   last or self.cont_name)

    def emit_codeinfo(self, code_info: PyCodeInfo) -> str:
        raise NotImplementedError

    def emit_instrs(self, instrs: t.List[Instr], with_head=True):

        def _op():
            for each in instrs:
                emit(each, self)

        if with_head:
            tmplt = "{}cdef int {} = 0"
            self += tmplt.format(self.prefix, self.last_cont_name)
            self += tmplt.format(self.prefix, self.cont_name)
            self += tmplt.format(self.prefix, self.lineno_name)
            self += "{}# Control flow graph splitted".format(
                self.prefix)
            self += "{}while True:".format(self.prefix)
            with indent(self):
                _op()
        else:
            _op()


@singledispatch
def emit(a: Instr, self: CodeEmitter):
    raise NotImplementedError(a)


def emit_const(self: CodeEmitter, r: object):
    if isinstance(r, (ValSymbol, Symbol)):
        var_name = self.declare_symbol(r.s)
        return var_name
    elif isinstance(r, PyCodeInfo):
        return self.emit_codeinfo(r)
    return repr(r)


def emit_repr(self: CodeEmitter, r: Repr) -> str:
    # TODO:
    if isinstance(r, Const):
        return emit_const(self, r.val)
    elif isinstance(r, Reg):
        return self.mangle(r.n)
    else:
        raise TypeError(r)


@contextmanager
def indent(self: CodeEmitter):
    self.indent()
    try:
        yield
    finally:
        self.dedent()


@emit.register
def set_lineno(n: SetLineno, self: CodeEmitter):
    self += "{}{} = {}".format(self.prefix, self.lineno_name, n.lineno)


def phi_for_given_branch(self, var_dict):
    for k, r in var_dict.items():
        v = emit_repr(self, r)
        k = self.mangle(k)
        self += "{}{} = {}".format(self.prefix, k, v)


def phi(self, phi_dict):

    def app(_self, _token, _var_dict):
        _self += "{}{}:".format(_self.prefix, _token)
        with indent(_self):
            phi_for_given_branch(_self, _var_dict)

    head, *init, end = phi_dict.items()

    token = "if {} == {}".format(head[0], self.last_cont_name)
    app(self, token, head[1])

    for come_from, var_dict in init:
        token = "elif {} == {}".format(come_from, self.last_cont_name)
        app(self, token, var_dict)

    self += "# must from label {}".format(head[0])
    app(self, "else", end[1])


@emit.register
def label(n: BeginBlock, self: CodeEmitter):
    self += "{}if {} == {}:".format(self.prefix, n.label,
                                    self.cont_name)

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
def end(_: EndBlock, self: CodeEmitter):
    self.set_last_cont(self.cont_name)
    self += "{}break".format(self.prefix)
    self.dedent()


@emit.register(PyGlob)
def ass_glob(n: t.Union[PyGlob], self: CodeEmitter):
    if not n.target:
        return
    tag = self.mangle(n.target)
    qual = n.qual
    assert not qual, "Python Globals not using qualname yet."
    name = n.name
    glob_name = self.glob[name]
    self += "{}{} = {}".format(self.prefix, tag, glob_name)


@emit.register(CyGlob)
def ass_glob(n: t.Union[CyGlob], self: CodeEmitter):
    if not n.target:
        return
    tag = self.mangle(n.target)
    qual = n.qual
    if qual:
        self += "{}{} = {}.{}".format(self.prefix, tag, qual, n.name)
    else:
        self += "{}{} = {}".format(self.prefix, tag, n.name)


@emit.register
def ret(r: Return, self: CodeEmitter):
    self += "{}return {}".format(self.prefix, emit_repr(self, r.val))


@emit.register
def set_cont(c: Jmp, self: CodeEmitter):
    prefix = self.prefix
    self += "{}{} = {}".format(prefix, self.cont_name, c.label)
    self.set_last_cont()
    self += "{}break".format(prefix)


@emit.register
def set_conf_if(c: JmpIf, self: CodeEmitter):
    self += "{}if {}:".format(self.prefix, emit_repr(self, c.cond))
    with indent(self):
        prefix = self.prefix
        self += "{}{} = {}".format(prefix, self.cont_name, c.label)
        self.set_last_cont()
        self += "{}break".format(prefix)


@emit.register
def store(st: Store, self: CodeEmitter):
    ptr_tag = self.mangle(st.target)
    val = emit_repr(self, st.val)
    self += "{}{}[0] = {}".format(self.prefix, ptr_tag, val)


@emit.register
def load(l: Load, self: CodeEmitter):
    tag = self.mangle(l.target)
    ptr = emit_repr(self, l.reg)
    self += "{}{} = {}[0]".format(self.prefix, tag, ptr)


@emit.register
def ass(a: Ass, self: CodeEmitter):
    tag = self.mangle(a.target)
    val = emit_repr(self, a.val)
    self += "{}{} = {}".format(self.prefix, tag, val)


@emit.register
def app(a: App, self: CodeEmitter):
    tag = ""
    if a.target:
        tag = "{} = ".format(self.mangle(a.target))
    args = ', '.join(map(lambda x: emit_repr(self, x), a.args))
    f = emit_repr(self, a.f)
    self += "{}{}{}({})".format(self.prefix, tag, f, args)
