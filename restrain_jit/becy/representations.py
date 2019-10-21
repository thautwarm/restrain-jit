from enum import Enum, auto as _auto
import abc
import typing as t
from dataclasses import dataclass


class Repr:
    pass


@dataclass(frozen=True, order=True)
class Reg(Repr):
    n:str
    pass


@dataclass(frozen=True, order=True)
class Const(Repr):
    val:object
    pass
