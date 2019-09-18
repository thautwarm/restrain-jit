from restrain_jit.bejulia.functional import foreach, map
from restrain_jit.bejulia.julia_vm import JuVM
from restrain_jit.bejulia.jl_init import init

init()

jit = JuVM.func_info

foreach([1, 2, 3])(print)


@jit
def all_add2(lst):

    @map(lst)
    def ret(elt):
        return elt + 2

    return ret


import numpy as np
xs = np.arange(1000)
zs = all_add2(xs)
print(zs)

import timeit

from builtins import  map
def py_all_add2(lst):

    return list(map(lambda x: x + 2, lst))

import timeit

%timeit py_all_add2(xs)
%timeit all_add2(xs)

