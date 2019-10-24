from restrain_jit.becython.cy_loader import setup_pyx_for_cpp
from pyximport import pyximport
setup_pyx_for_cpp()
pyximport.install()
import restrain_jit.becython.cython_rts.hotspot
from restrain_jit.becython.cy_loader import compile_module
mod = """
cimport restrain_jit.becython.cython_rts.RestrainJIT as RestrainJIT
from restrain_jit.becython.cython_rts.hotspot cimport inttopy, pytoint, JITCounter
from libc.stdint cimport int64_t, int32_t, int16_t, int8_t
from libcpp.map cimport map as std_map
from libcpp.vector cimport vector as std_vector
from cython cimport typeof, final

cdef fused Arg1:
    object

cdef fused Arg2:
    object

cdef fused Arg3:
    object


cdef JITCounter counter
cdef object recompile_handler
cdef object global_abs

    
cpdef f(Arg1 x, Arg2 y, Arg3 z):
    if typeof(x) == typeof(object) or typeof(x) == typeof(object) or typeof(z) == typeof(object):
        counter[(type(x), type(y), type(z))] += 1
        if counter.times % 100 == 0:
            recompile_handler()
    return x + y + z
        
cpdef init(dict globs, dict _counter, _handler):
    global global_abs, counter, recompile_handler 
    global_abs = globs['abs']
    counter = JITCounter(_counter)
    recompile_handler = _handler
"""

mod = compile_module('m', mod)
mod.init(dict(abs=abs), {}, lambda : print("jit started!"))
print(mod.f(14514, 2, 3))
