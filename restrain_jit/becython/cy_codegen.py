from restrain_jit.becython.phi_vm import *
from io import StringIO
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


class CodeEmitter:
    lineno_name = "_restrain__lineno"
    cont_name = "_restrain__cont"
    last_cont_name = "_restrain__last_cont"
    tmp_head = '_res_tmp_'

    def __init__(self, io: StringIO, options: CodeGenOptions = None):
        self.prefixes = [""]

        tmp = self.tmp_head

        def mangle_rule():
            return "{}{}".format(tmp, len(mangle_map))

        mangle_map = self.mangle_map = MissingDict(mangle_rule)

        write = io.write

        def emit_line(line):
            write(line)
            write('\n')

        def change_io_target(new_io: StringIO):
            emit_line.__closure__[0].cell_contents = new_io.write

        self.emit_line = emit_line
        self.change_io_target = change_io_target

    @property
    def prefix(self):
        return self.prefixes[-1]

    def indent(self):
        self.prefixes.append(self.prefix + "    ")

    def dedent(self):
        self.prefixes.pop()

    def mangle(self, n: str):
        if n.isidentifier():
            return n
        return self.mangle_map[n]

    def __iadd__(self, other):
        self.emit_line(other)
        return self

    def set_cont(self, label_i):
        self += "{}{} = {}".format(self.prefix, self.last_cont_name,
                                   label_i)

    def set_last_cont(self, last=None):
        self += "{}{} = {}".format(self.prefix, self.last_cont_name,
                                   last or self.cont_name)

    def emit(self, instrs: t.List[Instr], with_head=True):

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


def emit_repr(self: CodeEmitter, r: Repr) -> str:
    # TODO:
    if isinstance(r, Const):
        return repr(r.val)
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


@emit.register(CyGlob)
@emit.register(PyGlob)
def ass_glob(n: t.Union[PyGlob, CyGlob], self: CodeEmitter):
    if n.target:
        tag = self.mangle(n.target)
        if n.qual:
            self += "{}{} = {}.{}".format(self.prefix, tag, n.qual,
                                          n.name)
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
