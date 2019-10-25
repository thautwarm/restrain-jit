from restrain_jit.becython.cy_loader import compile_module, setup_pyx_for_cpp
from pyximport import pyximport
setup_pyx_for_cpp()
pyximport.install()
import restrain_jit.becython.cython_rts.hotspot

mod = """
cimport cython
from libc cimport stdint
from cpython.ref cimport PyObject
from restrain_jit.becython.cython_rts.hotspot cimport pytoint, check_ptr_eq
cdef object o = None
ot = pytoint(cython.typeof(o)) 
cdef fused C: 
   int 
   float
   object

cdef class MyClass:
    pass

cdef f(C x):
    cdef int a = pytoint(cython.typeof(x))
    return a 

def g(C x):
   return f(x)

def h():
   z = cython.typeof(h)
   return check_ptr_eq(z, cython.typeof(object))  
"""

mod = compile_module('m', mod)
print(mod.h())

a = mod.g(mod.MyClass())
assert isinstance(a, int)
assert a == mod.g(mod.MyClass())

b = mod.g(1)
assert isinstance(b, int)
assert b == mod.g(1)

assert a != b
