from julia import core
from restrain_jit.bejulia.simple_julia_py import get_julia
from restrain_jit.bejulia.jl_protocol import bridge, Aware
import ctypes

libjulia = get_julia().lib

jl_main = ctypes.c_void_p.in_dll(libjulia, "jl_main_module")

# libjulia.jl_exception_occurred.restype = ctypes.c_void_p

# jl_get_global = libjulia.jl_get_global
# jl_get_global.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
# jl_get_global.restype = ctypes.c_void_p
#
# jl_call0 = libjulia.jl_call0
# jl_call0.argtypes = [ctypes.c_void_p]
# jl_call0.restype = ctypes.c_void_p
#
# jl_symbol = libjulia.jl_symbol
# jl_symbol.argtypes = [ctypes.c_char_p]
# jl_symbol.restype = ctypes.c_void_p

libjulia.jl_eval_string(b"import RestrainJIT")
libjulia.jl_eval_string(b"aware! = RestrainJIT.init!()")
libjulia.jl_eval_string(b'print(1)')
libjulia.jl_eval_string(b'println(PyCall)')
libjulia.jl_eval_string(b'print(2)')


def init():

    # restrain_jl_side_aware_ = jl_get_global(jl_main,
    #                                         jl_symbol(b"aware!"))

    def aware_(val):
        bridge.append(val)
        libjulia.jl_eval_string(b"aware!()")
        return bridge.pop()

    Aware.f = aware_
