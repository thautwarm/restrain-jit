from restrain_jit.becython.cy_loader import setup_pyx_for_cpp
from pyximport import pyximport

setup_pyx_for_cpp()
pyximport.install()
import restrain_jit.becython.cython_rts.hotspot
from restrain_jit.becython.cy_loader import compile_module

mod = """
cimport restrain_jit.becython.cython_rts.RestrainJIT as RestrainJIT
from restrain_jit.becython.cython_rts.hotspot cimport pytoint, inttoptr
from libc.stdint cimport int64_t
from libcpp.cast cimport reinterpret_cast

# method type
ctypedef object (*method_t)(object, object, object)

# method lookup type
ctypedef method_t (*method_get_t)(int64_t, int64_t, int64_t)

# method look up ptr
cdef method_get_t method_get

# to avoid params have conflicts against 'type'
cdef inline method_t method_get_invoker(x, y, z):
    func = method_get(pytoint(type(x)), pytoint(type(y)), pytoint(type(x)))
    return func

cdef class ty_f:
    # python compatible method to change 'method look up ptr'
    cpdef mut_method_get(self, int64_t f):
        global method_get
        method_get = reinterpret_cast[method_get_t](inttoptr(f))
        
    def __call__(self, x, y, z):
        method = method_get_invoker(x, y, z)
        return method(x, y, z)
"""

mod = compile_module("a", mod)
