import abc
import typing as t
from ast import arg

Instr = t.TypeVar("Instr")
Repr = t.TypeVar("Repr")


class AM(t.Generic[Instr, Repr]):
    @classmethod
    @abc.abstractmethod
    def reg_of(cls, n: str):
        raise NotImplemented

    @abc.abstractmethod
    def release(self, name: str) -> None:
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


def reg_of(name: str):
    return lambda vm: vm.reg_of(name)


def release(name: str):
    return lambda vm: vm.release(name)


def alloc():
    return lambda vm: vm.alloc()


def add_instr(instr: Instr):
    def apply(vm):
        a = vm.alloc()
        vm.add_instr(a, instr)
        return vm.reg_of(vm)

    return apply


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


def run_machine(gen: t.Generator, vm: AM):
    """
    top level of abstract interpretion
    """
    binder = gen.send(None)
    v = binder(vm)
    try:
        while True:
            binder = gen.send(v)
            v = binder(vm)
    except StopIteration as e:
        return e.value
