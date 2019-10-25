from restrain_jit.becython.cy_loader import setup_pyx_for_cpp
from pyximport import pyximport

setup_pyx_for_cpp()
pyximport.install()
import restrain_jit.becython.cython_rts.hotspot
from restrain_jit.becython.cy_loader import compile_module

mod = """
cimport restrain_jit.becython.cython_rts.RestrainJIT as RestrainJIT
from restrain_jit.becython.cython_rts.hotspot cimport pytoint 
print(RestrainJIT.get_symbol("attr"))
print(RestrainJIT.get_symbol("attra"))

cpdef int f(x):
    return pytoint(type(x))
"""

mod = compile_module('m', mod)
print(mod.f(10))
print(mod.f(10))
print(mod.f(""))
print(mod.f(""))
print(mod.f(1.0))
print(mod.f(1.0))

