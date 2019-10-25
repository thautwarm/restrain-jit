import sys
from restrain_jit.becython.cy_loader import setup_pyx_for_cpp
from pyximport import pyximport
from timeit import timeit

from restrain_jit.becython.cython_vm import Options

setup_pyx_for_cpp()
pyximport.install()
import restrain_jit.becython.cython_rts.hotspot
from restrain_jit.becython.cy_jit_ext_template import mk_module_code

from restrain_jit.becython.cy_jit import JITSystem
jit_sys = JITSystem()


@jit_sys.jitdata
class IntRef:
    a: int


intref = IntRef(1)
print(intref.a)


@jit_sys.jit
def f(x, v):
    x.a = v


class IntRef2:
    a: int


intref2 = IntRef2()

intref2.a = 0


def g(x, v):
    x.a = v


template = "f(x, 10)"


def test(f, data):
    t = timeit(template, number=10000000, globals=dict(f=f, x=data))
    print(f, 'costs', t)


for i in range(1000):
    f(intref, 10)

for i in range(1000):
    f(intref2, 10)

print('stats:')
test(f, intref)
test(g, intref)

print('stats:')
test(f, intref2)
test(g, intref2)

fn_place = jit_sys.fn_place_index[id(f)]
method, *_ = fn_place.methods.items()

load_ty = fn_place.call_recorder.load_type
print('argtype:', tuple(map(load_ty, method[0])), 'addr:', hex(method[1]))
