from restrain_jit.becython.cy_loader import setup_pyx_for_cpp
from pyximport import pyximport
setup_pyx_for_cpp()
pyximport.install()
import restrain_jit.becython.cython_rts.hotspot
from restrain_jit.becython.cy_loader import compile_module
mod = """
cimport restrain_jit.becython.cython_rts.RestrainJIT as RestrainJIT
from restrain_jit.becython.cython_rts.hotspot cimport pytoint, inttoptr
from libc.stdint cimport uint64_t, int64_t, int32_t, int16_t, int8_t
from libcpp.map cimport map as std_map
from libcpp.vector cimport vector as std_vector
from libcpp.cast cimport static_cast, reinterpret_cast

from cython cimport typeof, final
from cpython.ref cimport PyObject
    
cdef object call(_, x, y, z):
    return x + y + z
    
ctypedef object (*method_t)(object, object, object, object)
ctypedef method_t (*method_get_t)(int64_t, int64_t, int64_t)

cdef method_t get_method(int64_t x, int64_t y, int64_t z):
    if pytoint(type(x)) == pytoint(int):
        return call
    return call    

cdef method_get_t method_get = get_method
    
cpdef mut_method_get(int64_t f):
    global method_get
    method_get = reinterpret_cast[method_get_t](inttoptr(f))
    
cdef class ty_f:
    def __call__(self, x, y, z):
        func = method_get(pytoint(type(x)), pytoint(type(y)), pytoint(type(x)))
        return func(self, x, y, z)

cdef method_t getter2(x, y, z):
    return call


f2_addr = reinterpret_cast[int64_t](<void*>getter2) 
f = ty_f()
"""

from timeit import timeit
mod = compile_module('m', mod)

print(mod.f(14514, 2, 3))

template = "f(1, 2, 3)"


def f(x, y, z):
    return x + y + z


def test(f):
    t = timeit(template, number=10_000_000, globals=dict(f=f))
    print(f, 'costs', t)


test(mod.f)
test(f)

mod.mut_method_get(mod.f2_addr)

test(mod.f)
test(f)

