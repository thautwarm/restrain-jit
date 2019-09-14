from __future__ import annotations
import typing as t
import abc
from abc import ABC, ABCMeta

Repr = t.TypeVar("Repr")
A = t.TypeVar("A")
B = t.TypeVar("B")
C = t.TypeVar("C")


class IR(t.SupportsAbs[Repr]):
    pass

class Less(abc.ABC):
    def __init__(self, ev: Eval):
        self.ev = ev

    def bin_op(self, op, a: IR[A], b : IR[A]):
        raise NotImplemented

    def func(self, args, ):
        pass
class Eval(abc.ABC):
    pass