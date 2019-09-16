"""
Julia unsafe APIs.
No exception checks, no wrapping, etc.
"""
from julia import Main
from julia.core import get_libjulia, Julia
import ctypes

bridge = None

jl = Julia()
api = jl.api
mapi = get_libjulia()
libjulia = mapi.libjulia

_call = jl._call


def eval_no_box(src):
    if src is None:
        return None
    ans = _call(src)
    if not ans:
        return None
    return ans


jl_main = ctypes.c_void_p.in_dll(libjulia, "jl_main_module")

jl_get_field = mapi.jl_get_field
jl_get_global = mapi.jl_get_global

jl_get_field.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
jl_get_field.restype = ctypes.c_void_p

jl_get_global.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
jl_get_global.restype = ctypes.c_void_p

jl_symbol = mapi.jl_symbol
jl_symbol.argtypes = [ctypes.c_char_p]
jl_symbol.restype = ctypes.c_void_p
jl_call1 = mapi.jl_call1
jl_call1.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
jl_call1.restype = ctypes.c_void_p

jl_call2 = mapi.jl_call2
jl_call2.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.py_object]
jl_call2.restype = ctypes.c_void_p

jl_box_voidpointer = mapi.jl_box_voidpointer

jl_box_voidpointer.argtypes = [ctypes.py_object]
jl_box_voidpointer.restype = ctypes.c_void_p

jl_call2py = mapi.jl_call2
jl_call2py.argtypes = [
    ctypes.c_void_p, ctypes.c_void_p, ctypes.py_object
]
jl_call2py.restype = ctypes.c_void_p

jl_convert = jl_get_global(jl_main, jl_symbol(b'convert'))
jl_println = jl_get_global(jl_main, jl_symbol(b"println"))
JLPyObject = jl._PyObject

eval_no_box("import RestrainJIT")
jl_restrain_jit = eval_no_box("RestrainJIT")
py_obj = ctypes.py_object

_as_pyobj = jl._as_pyobj
cast = ctypes.cast
c_void_p = ctypes.c_void_p
pointer = ctypes.pointer


def to_py(py: object):
    return _as_pyobj(py)


def aware():
    pass


# def callpy1(f, py: object):
#     py = cast(pointer(py_obj(py)), c_void_p)
#     # py = jl_box_voidpointer(py_obj(py))
#     # print('emmm')
#     return jl_call1(f, jl_call1(JLPyObject, py))

# print(eval_no_box(":a"))
# a = jl_symbol(b"eval")
# print(to_py(a))
# pl = jl_symbol(b"println")
#
# c = jl_get_global(jl_main, pl)
# println = eval_no_box("println")
# jl_call1(println, jl_main)
# jl_call1(println, c)
