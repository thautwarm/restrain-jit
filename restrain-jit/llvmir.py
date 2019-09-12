from dataclasses import dataclass
import typing as t
import abc


class LLType:
    pass


class FirstClassType(LLType):
    pass


@dataclass
class VoidType:
    pass


@dataclass(frozen=True)
class FuncType(LLType):
    ret_ty : LLType
    params : t.List[LLType]


@dataclass(frozen=True)
class IntType(FirstClassType):
    bit: int


@dataclass(frozen=True)
class FloatType(FirstClassType):
    bit: int


@dataclass(frozen=True)
class PtrType(FirstClassType):
    ty: LLType


@dataclass(frozen=True)
class LabelType(FirstClassType):
    pass


@dataclass(frozen=True)
class ArrayType(FirstClassType):
    n: int
    ty: LLType


@dataclass(frozen=True)
class StructType(FirstClassType):
    ty_list: t.List[LLType]


@dataclass(frozen=True)
class NamedType(FirstClassType):
    n: str
