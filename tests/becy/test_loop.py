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
Options['log-phi'] = True

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
    t = timeit(template, number=1000, globals=dict(f=f, seq=[*range(1000)]))
    print(f, 'costs', t)


print(jit_sys.fn_place_index[id(f)].base_method_code)

print(f(list(range(100)), 3))
test(f)
test(g)

fn_place = jit_sys.fn_place_index[id(f)]
call_records = fn_place.call_records
vec = (call_records.get())
print(call_records.load_type(vec[0][0]))


