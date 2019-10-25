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

# DEBUG['stack-vm'] = True
# Options['log-phi'] = True

# show generated code for debug
jit_sys.store_base_method_log = True


@jit_sys.jit
def f(x, y):
    if x < y:
        return x + y + y + y + x
    return 10


def g(x, y):
    if x < y:
        return x + y + y + y + x
    return 10


template = "f(2, 3)"


def test(f):
    t = timeit(template, number=10_000_000, globals=dict(f=f))
    print(f, 'costs', t)


print(f(1, 2))
test(f)
test(g)

test(f)
test(g)

template = "f(2.0, 3.0)"


test(f)
test(g)

test(f)
test(g)
