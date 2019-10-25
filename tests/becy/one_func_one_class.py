from restrain_jit.becython.cy_loader import compile_module, setup_pyx_for_cpp
from timeit import timeit
# from pyximport import pyximport
# setup_pyx_for_cpp()
# pyximport.install()
# import restrain_jit.becython.cython_lib.hotspot

mod = """
cimport cython
cdef class ty_S:
    def __call__(self, x, y, z):
        return x + y + z

@cython.final
cdef class ty_F:
    def __call__(self, x, y, z):
            return x + y + z

s = ty_S()
f = ty_F()

cpdef F(x, y, z):
    return x + y + z
    
cdef class ty_Si:
    def __call__(self, int x, int y, int z):
        return x + y + z

@cython.final
cdef class ty_Fi:
    def __call__(self, int x, int y, int z):
            return x + y + z

si = ty_Si()
fi = ty_Fi()

cpdef Fi(int x, int y, int z):
    return x + y + z
    

cdef fused ty_f_Arg1:
    object

cdef fused ty_f_Arg2:
    object

cdef fused ty_f_Arg3:
    object

    
cpdef ff(ty_f_Arg1 x, ty_f_Arg2 y, ty_f_Arg3 z):
    return x + y + z
        
"""

mod = compile_module("a", mod)
print(mod.s(1, 2, 3))


def f(x, y, z):
    return x + y + z


template = "f(1, 2, 3)"


def test(f):
    t = timeit(template, number=10_000_000, globals=dict(f=f))
    print(f, 'costs', t)
print(mod.ff(1, 2, 3))

test(mod.s)
test(mod.f)
test(mod.F)
test(f)
test(mod.si)
test(mod.fi)
test(mod.Fi)
test(mod.ff)
