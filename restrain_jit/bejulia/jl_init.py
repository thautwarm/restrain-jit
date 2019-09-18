from julia import Main
from julia.core import get_libjulia, _LIBJULIA
from restrain_jit.bejulia.jl_protocol import bridge, Aware
import ctypes

mapi = _LIBJULIA
libjulia = mapi.libjulia

jl_main = ctypes.c_void_p.in_dll(libjulia, "jl_main_module")

jl_get_global = mapi.jl_get_global
jl_get_global.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
jl_get_global.restype = ctypes.c_void_p

jl_call0 = mapi.jl_call0
jl_call0.argtypes = [ctypes.c_void_p]
jl_call0.restype = ctypes.c_void_p

jl_symbol = mapi.jl_symbol
jl_symbol.argtypes = [ctypes.c_char_p]
jl_symbol.restype = ctypes.c_void_p

Main.eval("import RestrainJIT")
Main.eval("restrain_jl_side_aware! = RestrainJIT.mk_restrain_infr!()")


def init():

    restrain_jl_side_aware_ = jl_get_global(
        jl_main, jl_symbol(b"restrain_jl_side_aware!"))

    def aware_(val, func_id):
        bridge.append((func_id, val))
        jl_call0(restrain_jl_side_aware_)
        return bridge.pop()

    Aware.f = aware_
