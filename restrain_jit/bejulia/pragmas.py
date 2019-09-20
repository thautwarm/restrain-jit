import typing as t
T = t.TypeVar("T")


class _Const(t.Generic[T]):

    def __getitem__(self, item: T) -> T:
        return self


const = _Const()
