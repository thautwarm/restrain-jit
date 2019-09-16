import typing as t
import types
from dataclasses import dataclass
Instr = t.TypeVar("Instr")


@dataclass
class PyCodeInfo(t.Generic[Instr]):
    code: types.CodeType
    glob_deps: t.Tuple[str]
    instrs: t.List[t.Tuple[str, Instr]]
    freevars: t.Tuple[str, ...]
    cellvars: t.Tuple[str, ...]
    bounds: t.Tuple[str, ...]
    filename: str
    lineno: int
    consts: t.Tuple[object, ...]
    argcount: int
    kwonlyargcount: int
