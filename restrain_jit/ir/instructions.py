from enum import Enum, auto as _auto
import abc
import typing as t
from dataclasses import dataclass


from restrain_jit.ir.representations import *


class VarScope(Enum):
    Unknown = _auto()
    Local = _auto()
    Global = _auto()
    Free = _auto()
    pass


class Instr:
    pass


@dataclass
class App(Instr):
    argn:int
    pass


@dataclass
class Var(Instr):
    name:str
    scope:VarScope
    pass


@dataclass
class Val(Instr):
    val:object
    pass


@dataclass
class Ass(Instr):
    name:str
    scope:VarScope
    pass


@dataclass
class Ref(Instr):
    name:str
    pass


@dataclass
class Deref(Instr):
    name:str
    pass


@dataclass
class Setref(Instr):
    name:str
    pass


@dataclass
class JmpIf(Instr):
    label:str
    cond:t.Union[Reg,Const]
    pass


@dataclass
class JmpIfPush(Instr):
    label:str
    cond:t.Union[Reg,Const]
    leave:t.Union[Reg,
    Const]
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
class Dup(Instr):
    pass


@dataclass
class Peek(Instr):
    offset:int
    pass


@dataclass
class Return(Instr):
    pass


@dataclass
class Yield(Instr):
    pass


@dataclass
class YieldFrom(Instr):
    pass


@dataclass
class YieldFrom(Instr):
    pass
