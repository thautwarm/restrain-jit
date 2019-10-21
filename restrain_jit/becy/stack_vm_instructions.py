from enum import Enum, auto as _auto
import abc
import typing as t
from dataclasses import dataclass


class Instr:
    pass


class Repr:
    pass


@dataclass(frozen=True, order=True)
class A:
    lhs:t.Optional[str]
    rhs:Instr
    pass


@dataclass(frozen=True, order=True)
class Reg(Repr):
    n:str
    pass


@dataclass(frozen=True, order=True)
class Const(Repr):
    val:object
    pass


@dataclass(frozen=True, order=True)
class App(Instr):
    f:Repr
    args:t.List[Repr]
    pass


@dataclass(frozen=True, order=True)
class Ass(Instr):
    reg:Reg
    val:Repr
    pass


@dataclass(frozen=True, order=True)
class Load(Instr):
    reg:Reg
    pass


@dataclass(frozen=True, order=True)
class Store(Instr):
    reg:Reg
    val:Repr
    pass


@dataclass(frozen=True, order=True)
class JmpIf(Instr):
    label:str
    cond:Repr
    pass


@dataclass(frozen=True, order=True)
class JmpIfPush(Instr):
    label:str
    cond:Repr
    leave:Repr
    pass


@dataclass(frozen=True, order=True)
class Jmp(Instr):
    label:str
    pass


@dataclass(frozen=True, order=True)
class Label(Instr):
    label:str
    pass


@dataclass(frozen=True, order=True)
class Peek(Instr):
    offset:int
    pass


@dataclass(frozen=True, order=True)
class Return(Instr):
    val:Repr
    pass


@dataclass(frozen=True, order=True)
class Push(Instr):
    val:Repr
    pass


@dataclass(frozen=True, order=True)
class Pop(Instr):
    pass


@dataclass(frozen=True, order=True)
class PyGlob(Instr):
    qual:str
    name:str
    pass


@dataclass(frozen=True, order=True)
class CyGlob(Instr):
    qual:str
    name:str
    pass


@dataclass(frozen=True, order=True)
class UnwindBlock(Instr):
    instrs:t.List[A]
    pass


@dataclass(frozen=True, order=True)
class PopException(Instr):
    must:bool
    pass
