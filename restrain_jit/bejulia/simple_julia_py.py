import ctypes
import json
from pathlib import Path
from functools import lru_cache
from typing import Union


def check_config(conf: dict):
    # TODO
    pass


@lru_cache()
def get_conf(path: str):
    try:
        path = Path(path).expanduser() / "info.json"
        with path.open() as info:
            conf = json.load(info)
            check_config(conf)
            return conf
    except IOError:
        raise IOError(
            "Didn't find out correct configurations for Restrain at {}".
            format(path.absolute()))


class JuliaPreLoad:

    def __init__(self, init, lib):
        self.init = init
        self.lib = lib


def get_jl_lib(conf) -> JuliaPreLoad:
    jl = conf["julia"]
    lib_path = jl["lib"]
    sys_image = jl["image"]
    binary = jl["bin"]

    lib = ctypes.PyDLL(lib_path, ctypes.RTLD_GLOBAL)
    lib.jl_eval_string.argtypes = [ctypes.c_char_p]
    lib.jl_eval_string.restype = ctypes.c_void_p

    try:
        init = lib.jl_init_with_image
    except AttributeError:
        init = lib.jl_init_with_image__threading

    return JuliaPreLoad(
        lambda: init(binary.encode(), sys_image.encode()), lib)


def get_julia(julia: Union[JuliaPreLoad, str] = '~/.restrain'):
    if isinstance(julia, str):
        conf = get_conf(julia)
        return get_julia(get_jl_lib(conf))
    assert isinstance(julia, JuliaPreLoad)
    julia.init()
    julia.lib.jl_eval_string(b'try using PyCall catch e; println(e) end')
    julia.lib.jl_eval_string(b'println(100)')

    return julia
