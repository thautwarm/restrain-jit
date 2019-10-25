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
def f(seq, init):
    n = len(seq)
    i = 0
    while i < n:
        init = init + seq[i]
        i = i + 1
    return init


def g(seq, init):
    n = len(seq)
    i = 0
    while i < n:
        init = init + seq[i]
        i = i + 1

    return init


template = "f(seq, 12)"


def test(f):
    t = timeit(template, number=30000, globals=dict(f=f, seq=[*range(1000)]))
    print(f, 'costs', t)


test(f)
test(g)
test(f)
test(g)


@jit_sys.jit
def f(low, high, step):
    s = 0
    i = low
    while i < high:
        s = s + i
        i = i + step
    return s


def g(low, high, step):
    s = 0
    i = low
    while i < high:
        s = s + i
        i = i + step
    return s


template = "f(0, 1000, 3)"


def test(f):
    t = timeit(template, number=30000, globals=dict(f=f, seq=[*range(1000)]))
    print(f, 'costs', t)


test(f)
test(g)
test(f)
test(g)
