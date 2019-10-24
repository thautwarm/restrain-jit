import abc
import types
import typing as t
import bytecode
from restrain_jit.jit_info import PyCodeInfo, PyFuncInfo
from dataclasses import dataclass


@dataclass
class Symbol:
    s: str


@dataclass
class ValSymbol:
    s: str


Instr = t.TypeVar("Instr")
Repr = t.TypeVar("Repr")


class AM(t.Generic[Instr, Repr]):

    @abc.abstractmethod
    def yield_return(self, val: Repr):
        raise NotImplemented

    @abc.abstractmethod
    def set_lineno(self, lineno: int):
        raise NotImplemented

    @abc.abstractmethod
    def require_global(self, s: str):
        raise NotImplemented

    @abc.abstractmethod
    def meta(self) -> dict:
        raise NotImplemented

    @abc.abstractmethod
    def pop_exception(self, must: bool) -> Repr:
        raise NotImplemented

    @abc.abstractmethod
    def push_block(self, end_label: str) -> None:
        raise NotImplemented

    @abc.abstractmethod
    def pop_block(self) -> Repr:
        raise NotImplemented

    @abc.abstractmethod
    def last_block_end(self) -> str:
        raise NotImplemented

    @classmethod
    @abc.abstractmethod
    def reg_of(cls, n: str):
        raise NotImplemented

    @abc.abstractmethod
    def from_higher(self, qualifier: str, name: str):
        raise NotImplemented

    @abc.abstractmethod
    def from_lower(self, qualifier: str, name: str):
        raise NotImplemented

    @abc.abstractmethod
    def release(self, name: Repr) -> None:
        raise NotImplemented

    @abc.abstractmethod
    def alloc(self) -> str:
        raise NotImplemented

    @abc.abstractmethod
    def add_instr(self, tag: t.Union[None, str], instr: Instr) -> Repr:
        raise NotImplemented

    @abc.abstractmethod
    def pop(self) -> Repr:
        raise NotImplemented

    @abc.abstractmethod
    def push(self, r: Repr) -> None:
        raise NotImplemented

    @abc.abstractmethod
    def label(self, n: str) -> None:
        raise NotImplemented

    @abc.abstractmethod
    def jump_if(self, n: str, cond: Repr) -> None:
        raise NotImplemented

    @abc.abstractmethod
    def jump_if_push(self, n: str, cond: Repr, leave: Repr) -> None:
        raise NotImplemented

    @abc.abstractmethod
    def jump(self, n: str) -> None:
        raise NotImplemented

    @abc.abstractmethod
    def peek(self, n: int) -> Repr:
        raise NotImplemented

    @abc.abstractmethod
    def assign(self, reg: str, v: Repr):
        raise NotImplemented

    @abc.abstractmethod
    def load(self, reg: str) -> Repr:
        raise NotImplemented

    @abc.abstractmethod
    def store(self, reg: str, val: Repr) -> None:
        raise NotImplemented

    @abc.abstractmethod
    def app(self, f: Repr, args: t.List[Repr]) -> Repr:
        raise NotImplemented

    @abc.abstractmethod
    def const(self, val: object) -> Repr:
        raise NotImplemented

    @abc.abstractmethod
    def from_const(self, val: Repr) -> object:
        raise NotImplemented

    @abc.abstractmethod
    def ret(self, val: Repr) -> None:
        raise NotImplemented

    @classmethod
    @abc.abstractmethod
    def code_info(cls, code: bytecode.Bytecode) -> PyCodeInfo[Instr]:
        raise NotImplemented

    @classmethod
    @abc.abstractmethod
    def func_info(cls, func: types.FunctionType):
        raise NotImplemented

    @abc.abstractmethod
    def get_module(self) -> types.ModuleType:
        raise NotImplemented


def code_info(code: bytecode.Bytecode):
    return lambda vm: vm.code_info(code)


def func_info(fn: types.FunctionType):
    return lambda vm: vm.code_info(fn)


def pop_exception(must: bool = False) -> Repr:
    return lambda vm: vm.pop_exception(must)


def require_global(a: str):
    return lambda vm: vm.require_global(a)


def meta():
    return lambda vm: vm.meta()


def last_block_end():
    return lambda vm: vm.last_block_end()


def push_block(r: str):
    return lambda vm: vm.push_block(r)


def pop_block():
    return lambda vm: vm.pop_block()


def from_const(r: Repr):
    return lambda vm: vm.from_const(r)


def ret(val: Repr):
    return lambda vm: vm.ret(val)


def const(val: object):
    return lambda vm: vm.const(val)


def reg_of(name: str):
    return lambda vm: vm.reg_of(name)


def release(name: Repr):
    return lambda vm: vm.release(name)


def alloc():
    return lambda vm: vm.alloc()


def add_instr(instr: Instr):

    def apply(vm):
        a = vm.alloc()
        vm.add_instr(a, instr)
        return vm.reg_of(vm)

    return apply


def from_higher(qualifier: str, name: str):
    return lambda vm: vm.from_higher(qualifier, name)


def from_lower(qualifier: str, name: str):
    return lambda vm: vm.from_lower(qualifier, name)


def pop() -> Repr:
    return lambda vm: vm.pop()


def push(r: Repr):
    return lambda vm: vm.push(r)


def label(n: str):
    return lambda vm: vm.label(n)


def jump_if(n: str, cond: Repr):
    return lambda vm: vm.jump_if(n, cond)


def jump_if_push(n: str, cond: Repr, leave: Repr):
    return lambda vm: vm.jump_if_push(n, cond, leave)


def jump(n: str):
    return lambda vm: vm.jump(n)


def peek(n: int):
    return lambda vm: vm.peek(n)


def assign(reg: str, v: Repr):
    return lambda vm: vm.assign(reg, v)


def load(reg: str) -> Repr:
    return lambda vm: vm.load(reg)


def store(reg: str, val: Repr):
    return lambda vm: vm.store(reg, val)


def app(f: Repr, args: t.List[Repr]):
    return lambda vm: vm.app(f, args)


def get_module():
    return lambda vm: vm.get_module()


def set_lineno(i):
    return lambda vm: vm.set_lineno(i)


def yield_return(val):
    return lambda vm: vm.yield_return(val)


def run_machine(gen: t.Generator, vm: AM):
    """
    top level of abstract interpretion
    """
    v = None
    send = gen.send
    try:
        while True:
            binder = send(v)
            v = binder(vm)
    except StopIteration as e:
        return e.value
