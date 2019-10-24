from enum import Enum, auto as _auto
import abc
import typing as t
from dataclasses import dataclass


from restrain_jit.becython.representations import *


class Instr:
    pass


@dataclass(frozen=True, order=True)
class SetLineno(Instr):
    lineno:int
    pass


@dataclass(frozen=True, order=True)
class App(Instr):
    target:t.Optional[str]
    f:Repr
    args:t.List[Repr]
    pass


@dataclass(frozen=True, order=True)
class Ass(Instr):
    target:t.Optional[str]
    val:Repr
    pass


@dataclass(frozen=True, order=True)
class Load(Instr):
    target:t.Optional[str]
    reg:Reg
    pass


@dataclass(frozen=True, order=True)
class Store(Instr):
    target:t.Optional[str]
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
class BeginBlock(Instr):
    label:object
    phi:t.Dict[object,t.Dict[str,Repr]]
    pass


@dataclass(frozen=True, order=True)
class EndBlock(Instr):
    pass


@dataclass(frozen=True, order=True)
class Return(Instr):
    val:Repr
    pass


@dataclass(frozen=True, order=True)
class PyGlob(Instr):
    target:t.Optional[str]
    qual:str
    name:str
    pass
