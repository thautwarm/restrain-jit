from restrain_jit.bejulia.functional import foreach, select
from restrain_jit.bejulia.julia_vm import JuVM
from restrain_jit.bejulia.jl_init import init

init()

jit = JuVM.func_info

foreach([1, 2, 3])(print)


@jit
def all_add2(lst):

    @select(lst)
    def ret(elt):
        return elt + 2

    return ret


import numpy as np
xs = np.arange(1000)
zs = all_add2(xs)
print(zs)

import timeit

from builtins import map


def py_all_add2(lst):

    # np.fromiter is the most efficient way to
    # create numpy array from python iterator
    return np.fromiter(
        map(lambda x: x + 2, lst), dtype=np.int32, count=len(lst))


import timeit

print(
    timeit.timeit(
        """
all_add2(xs)""",
        globals=dict(all_add2=all_add2, xs=xs),
        number=100000))

print(
    timeit.timeit(
        """
all_add2(xs)""",
        globals=dict(all_add2=py_all_add2, xs=xs),
        number=100000))
