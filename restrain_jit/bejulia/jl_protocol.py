"""
Julia unsafe APIs.
No exception checks, no wrapping, etc.
"""
from julia import Main
from julia.core import get_libjulia, _LIBJULIA
import ctypes

bridge = None
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

    def aware_(val):
        restrain_jl_side_aware_ = jl_get_global(
            jl_main, jl_symbol(b"restrain_jl_side_aware!"))
        global bridge
        bridge = val
        jl_call0(restrain_jl_side_aware_)
        return bridge

    return aware_


# jl_get_field = mapi.jl_get_field
# jl_get_field.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
# jl_get_field.restype = ctypes.c_void_p
# jl_convert = jl_get_global(jl_main, jl_symbol(b'convert'))
# jl_println = jl_get_global(jl_main, jl_symbol(b"println"))
# JLPyObject = jl._PyObject
# jl_call1 = mapi.jl_call1
# jl_call1.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
# jl_call1.restype = ctypes.c_void_p
#
# jl_call2 = mapi.jl_call2
# jl_call2.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.py_object]
# jl_call2.restype = ctypes.c_void_p
# jl_symbol = mapi.jl_symbol
# jl_symbol.argtypes = [ctypes.c_char_p]
# jl_symbol.restype = ctypes.c_void_p
