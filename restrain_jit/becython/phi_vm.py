from enum import Enum, auto as _auto
import abc
import typing as t
from dataclasses import dataclass


from restrain_jit.becython.representations import *


class Instr:
    pass


@dataclass(frozen=True, order=True)
class A:
    lhs:t.Optional[str]
    rhs:Instr
    pass


@dataclass(frozen=True, order=True)
class SetLineno(Instr):
    lineno:int
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
    label:object
    cond:Repr
    pass


@dataclass(frozen=True, order=True)
class Jmp(Instr):
    label:object
    pass


@dataclass(frozen=True, order=True)
class Label(Instr):
    label:object
    phi:t.Dict[object,t.Dict[Reg,Repr]]
    pass


@dataclass(frozen=True, order=True)
class Return(Instr):
    val:Repr
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
