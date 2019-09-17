from restrain_jit.bejulia.instructions import *
from restrain_jit.bejulia.representations import *
from restrain_jit.bejulia.jl_protocol import bridge, Aware
from restrain_jit.jit_info import PyCodeInfo, PyFuncInfo
from restrain_jit.abs_compiler import instrnames as InstrNames
from restrain_jit.abs_compiler.from_bc import abs_i_cfg
from restrain_jit.vm.am import AM, run_machine
from dataclasses import dataclass
from bytecode import Bytecode, ControlFlowGraph, Instr as PyInstr, CellVar, CompilerFlags
import typing as t
import types


def load_arg(x, cellvars, lineno):
    if x in cellvars:
        return PyInstr(InstrNames.LOAD_DEREF, CellVar(x), lineno=lineno)

    return PyInstr(InstrNames.LOAD_FAST, x, lineno=lineno)


def copy_func(f: types.FunctionType):
    # noinspection PyArgumentList
    nf = types.FunctionType(f.__code__, f.__globals__, None, None,
                            f.__closure__)
    nf.__defaults__ = f.__defaults__
    nf.__name__ = f.__name__
    nf.__qualname__ = f.__qualname__
    nf.__module__ = f.__module__
    nf.__kwdefaults__ = f.__kwdefaults__
    nf.__annotations__ = f.__annotations__
    nf.__dict__ = f.__dict__
    return nf


@dataclass
class JuVM(AM[Instr, Repr]):

    @classmethod
    def func_info(cls, func: types.FunctionType) -> types.FunctionType:
        code = Bytecode.from_code(func.__code__)
        codeinfo = cls.code_info(code)

        def r_compile():
            jit_func = Aware.f(self)
            bc = Bytecode(code)
            bc.clear()
            bc.filename = filename
            bc.append(PyInstr(InstrNames.LOAD_CONST, jit_func))
            bc.extend(
                [load_arg(each, cellvars, lineno) for each in argnames])
            bc.extend([
                PyInstr(InstrNames.CALL_FUNCTION, len(argnames)),
                PyInstr(InstrNames.RETURN_VALUE)
            ])
            start_func.__code__ = Bytecode(bc).to_code()
            start_func.__jit__ = jit_func
            return jit_func

        start_func = copy_func(func)
        start_func_code = Bytecode(code)
        # noinspection PyProtectedMember
        filename = code.filename
        lineno = code.first_lineno

        argnames = start_func_code.argnames
        cellvars = start_func_code.cellvars
        start_func_code.clear()
        start_func_code.filename = filename
        start_func_code.extend([
            PyInstr(InstrNames.LOAD_CONST, r_compile, lineno=lineno),
            PyInstr(InstrNames.CALL_FUNCTION, 0, lineno=lineno),
            *(load_arg(each, cellvars, lineno) for each in argnames),
            PyInstr(
                InstrNames.CALL_FUNCTION, len(argnames), lineno=lineno),
            PyInstr(InstrNames.RETURN_VALUE, lineno=lineno)
        ])
        self = PyFuncInfo(func.__name__, func.__module__,
                          func.__defaults__, func.__kwdefaults__,
                          func.__closure__, func.__globals__, codeinfo,
                          func, {})
        start_func.__code__ = start_func_code.to_code()
        start_func.__func_info__ = self
        start_func.__compile__ = r_compile
        start_func.__jit__ = None
        return start_func

    @classmethod
    def code_info(cls, code: Bytecode) -> PyCodeInfo[Repr]:
        glob_deps: t.Set[str] = set()
        for each in code:
            if isinstance(each, PyInstr) and each.name in (
                    InstrNames.LOAD_GLOBAL, InstrNames.STORE_GLOBAL):
                glob_deps.add(each.arg)

        cfg = ControlFlowGraph.from_bytecode(code)
        self = cls.empty()
        run_machine(abs_i_cfg(cfg), self)
        instrs = self.instrs
        instrs = self.pass_push_pop_inline(instrs)
        return PyCodeInfo(
            code.name, tuple(glob_deps), code.argnames, code.freevars,
            code.cellvars, code.filename, code.first_lineno,
            code.argcount, code.kwonlyargcount,
            bool(code.flags & CompilerFlags.GENERATOR),
            bool(code.flags & CompilerFlags.VARKEYWORDS),
            bool(code.flags & CompilerFlags.VARARGS), instrs)

    def pop_exception(self, must: bool) -> Repr:
        name = self.alloc()
        self.add_instr(name, PopException(must))
        return Reg(name)

    def meta(self) -> dict:
        return self._meta

    def last_block_end(self) -> str:
        return self.end_label

    def push_block(self, end_label: str) -> None:
        self.blocks.append((end_label, []))

    def pop_block(self) -> Repr:
        end_label, instrs = self.blocks.pop()
        regname = self.alloc()
        instr = UnwindBlock(instrs)
        self.add_instr(regname, instr)
        return Reg(regname)

    def from_const(self, val: Repr) -> object:
        assert isinstance(val, Const)
        return val.val

    def ret(self, val: Repr):
        return self.add_instr(None, Return(val))

    def const(self, val: object):
        return Const(val)

    @classmethod
    def reg_of(cls, n: str):
        return Reg(n)

    def from_higher(self, qualifier: str, name: str):
        regname = self.alloc()
        self.add_instr(regname, PyGlob(qualifier, name))
        return Reg(regname)

    def from_lower(self, qualifier: str, name: str):
        regname = self.alloc()
        self.add_instr(regname, JlGlob(qualifier, name))
        return Reg(regname)

    def app(self, f: Repr, args: t.List[Repr]) -> Repr:
        name = self.alloc()
        self.add_instr(name, App(f, args))
        return Reg(name)

    def store(self, n: str, val: Repr):
        self.add_instr(None, Store(Reg(n), val))

    def load(self, n: str) -> Repr:
        r = Reg(n)
        name = self.alloc()
        self.add_instr(name, Load(r))
        return Reg(name)

    def assign(self, n: str, v: Repr):
        self.add_instr(None, Ass(Reg(n), v))

    def peek(self, n: int):
        try:
            return self.st[-n - 1]
        except IndexError:
            name = self.alloc()
            self.add_instr(name, Peek(n))
            return name

    def jump(self, n: str):
        self.add_instr(None, Jmp(n))

    def jump_if_push(self, n: str, cond: Repr, leave: Repr):
        self.add_instr(None, JmpIfPush(n, cond, leave))

    def jump_if(self, n: str, cond: Repr):
        self.add_instr(None, JmpIf(n, cond))

    def label(self, n: str) -> None:
        self.add_instr(None, Label(n))

    def push(self, r: Repr) -> None:
        self.st.append(r)
        self.add_instr(None, Push(r))

    def pop(self) -> Repr:
        try:

            a = self.st.pop()
            self.add_instr(None, Pop())
        except IndexError:
            name = self.alloc()
            self.add_instr(name, Pop())
            a = Reg(name)
        return a

    def release(self, name: Repr):
        """
        release temporary variable
        """
        if not isinstance(name, Reg):
            return
        name = name.n
        if name in self.used:
            self.used.remove(name)
            self.unused.add(name)

    def alloc(self):
        """
        allocate a new temporary variable
        """
        if self.unused:
            return self.unused.pop()
        tmp_name = f"tmp-{len(self.used)}"
        self.used.add(tmp_name)
        return tmp_name

    def add_instr(self, tag, instr: Instr):
        self.instrs.append(A(tag, instr))
        return None

    _meta: dict

    # stack
    st: t.List[Repr]

    # instructions
    blocks: t.List[t.Tuple[t.Optional[str], t.List[A]]]

    # allocated temporary
    used: t.Set[str]
    unused: t.Set[str]

    @property
    def instrs(self):
        return self.blocks[-1][1]

    @property
    def end_label(self) -> t.Optional[str]:
        return self.blocks[-1][0]

    @classmethod
    def pass_push_pop_inline(cls, instrs):
        blacklist = set()
        i = 0
        while True:
            try:
                assign = instrs[i]
                k, v = assign.lhs, assign.rhs
            except IndexError:
                break
            if isinstance(v, UnwindBlock):
                v.instrs = cls.pass_push_pop_inline(v.instrs)
            if k is None and isinstance(v, Pop):
                j = i - 1
                while True:
                    assign = instrs[j]
                    k, v = assign.lhs, assign.rhs
                    if k is None and isinstance(v, Push):
                        blacklist.add(j)
                        blacklist.add(i)
                        i += 1
                        j -= 1
                        try:
                            assign = instrs[j]
                            k, v = assign.lhs, assign.rhs
                        except IndexError:
                            break
                        if k is None and isinstance(v, Push):
                            continue
                        break

                    else:
                        i += 1
                        break
            else:
                i = i + 1

        return [
            each for i, each in enumerate(instrs) if i not in blacklist
        ]

    @classmethod
    def empty(cls):
        return cls({}, [], [(None, [])], set(), set())
