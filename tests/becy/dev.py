from restrain_jit.becython.cy_loader import setup_pyx_for_cpp
from pyximport import pyximport
setup_pyx_for_cpp()
pyximport.install()
import restrain_jit.becython.cython_rts.RestrainJIT
from restrain_jit.becython.cy_loader import compile_module


mod = """
cimport restrain_jit.becython.cython_rts.RestrainJIT as RestrainJIT

print(RestrainJIT.num_func(10))
"""
mod = compile_module('m', mod)