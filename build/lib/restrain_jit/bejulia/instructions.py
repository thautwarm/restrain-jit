from enum import Enum, auto as _auto
import abc
import typing as t
from dataclasses import dataclass


from restrain_jit.bejulia.representations import *


class Instr:
    pass


@dataclass
class App(Instr):
    f:Repr
    args:t.List[Repr]
    pass


@dataclass
class Ass(Instr):
    reg:Reg
    val:Repr
    pass


@dataclass
class Load(Instr):
    reg:Reg
    pass


@dataclass
class Store(Instr):
    reg:Reg
    val:Repr
    pass


@dataclass
class JmpIf(Instr):
    label:str
    cond:Repr
    pass


@dataclass
class JmpIfPush(Instr):
    label:str
    cond:Repr
    leave:Repr
    pass


@dataclass
class Jmp(Instr):
    label:str
    pass


@dataclass
class Label(Instr):
    label:str
    pass


@dataclass
class Peek(Instr):
    offset:int
    pass


@dataclass
class Return(Instr):
    val:Repr
    pass


@dataclass
class Push(Instr):
    val:Repr
    pass


@dataclass
class Pop(Instr):
    pass


@dataclass
class PyGlob(Instr):
    qual:str
    name:str
    pass


@dataclass
class JlGlob(Instr):
    qual:str
    name:str
    pass


@dataclass
class UnwindBlock(Instr):
    instrs:t.List[t.Tuple[str,
    Instr]]
    pass


@dataclass
class PopException(Instr):
    must:bool
    pass
