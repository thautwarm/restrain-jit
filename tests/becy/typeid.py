from restrain_jit.becython.cy_loader import compile_module, setup_pyx_for_cpp
from pyximport import pyximport
setup_pyx_for_cpp()
pyximport.install()
import restrain_jit.becython.cython_lib.restrain_hotspot

mod = """
cimport cython
from libc cimport stdint
from cpython.ref cimport PyObject
cimport restrain_jit.becython.cython_lib.restrain_hotspot
from restrain_jit.becython.cython_lib.restrain_hotspot cimport JITMonitor

cdef extern from "<typeint.h>":
    stdint.int64_t pyobjtoint "ptrtoint"(object)

cdef fused C: 
   int 
   float
   object

cdef class MyClass:
    pass

cdef f(C x):
    cdef int a = pyobjtoint(cython.typeof(x))
    return a 

def g(C x): 
   return f(x) 
"""

mod = compile_module('m', mod)
a = mod.g(mod.MyClass())
assert isinstance(a, int)
assert a == mod.g(mod.MyClass())

b = mod.g(1)
assert isinstance(b, int)
assert b == mod.g(1)

assert a != b