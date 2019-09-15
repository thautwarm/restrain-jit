from enum import Enum, auto as _auto
import abc
import typing as t
from dataclasses import dataclass


class Repr:
    pass


@dataclass
class Reg(Repr):
    n:str
    pass


@dataclass
class Const(Repr):
    val:object
    pass
