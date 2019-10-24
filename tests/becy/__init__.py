import sys
from restrain_jit.becython.cy_loader import setup_pyx_for_cpp
from pyximport import pyximport
from timeit import timeit
setup_pyx_for_cpp()
pyximport.install()
import restrain_jit.becython.cython_rts.hotspot

from restrain_jit.becython.cy_jit_ext_template import mk_module_code
from restrain_jit.becython.cy_jit import JITSystem
jit_sys = JITSystem()

# DEBUG['stack-vm'] = True
# Options['log-phi'] = True


@jit_sys.jit
def f(x, y, z, k):
    return x + y + z + k


def g(x, y, z, k):
    return x + y + z + k


template = "f(2, 3, 4, 5)"


def test(f):
    t = timeit(template, number=10_000_000, globals=dict(f=f))
    print(f, 'costs', t)


print(f(1, 2, 3, 4))

test(f)
test(g)
