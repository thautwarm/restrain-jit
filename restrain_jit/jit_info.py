import typing as t
import types
from dataclasses import dataclass

Instr = t.TypeVar("Instr")


@dataclass
class PyCodeInfo(t.Generic[Instr]):
    name: str

    glob_deps: t.Tuple[str]
    argnames: t.List[str]
    freevars: t.List[str]
    cellvars: t.List[str]

    filename: str
    lineno: int

    argcount: int
    kwonlyargcount: int

    is_gen: bool
    has_var_kw: bool
    has_var_arg: bool

    instrs: t.List


@dataclass(unsafe_hash=True, order=True, repr=False)
class PyFuncInfo(t.Generic[Instr]):
    r_name: str
    r_module: str
    r_defaults: t.Optional[t.Tuple[object, ...]]
    r_kw_defaults: t.Optional[dict]
    r_closure: t.Optional[t.Tuple[object, ...]]
    r_globals: dict
    r_codeinfo: PyCodeInfo
    r_func: types.FunctionType
    r_options: dict
    r_attrnames: t.Tuple[str, ...]
