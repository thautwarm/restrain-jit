import typing as t
from typing import overload, Sequence

T = t.TypeVar("T")


class JList(t.Generic[T]):

    def __init__(self, jl):
        self.__jit__ = jl

    @overload
    def __getitem__(self, i: int) -> T:
        ...

    @overload
    def __getitem__(self, s: slice) -> Sequence[T]:
        ...

    def __getitem__(self, i: int) -> T:
        return JList.__getitem__.__jit__(self, i)

    def __setitem__(self, i: int, v: T):
        return JList.__setitem__.__jit__(self, i, v)

    def append(self, e: T) -> None:
        JList.append.__jit__(self, e)

    def pop(self) -> T:
        return JList.pop.__jit__(self)

    __jit__: object


class JDict:
    __jit__: object


class JTuple:
    __jit__: object


class JSet:
    __jit__: object
