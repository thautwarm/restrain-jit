## restrain-jit

The first and yet the only CPython compatible Python JIT, over the world.

```python
from restrain_jit.bejulia.functional import foreach, map
from restrain_jit.bejulia.julia_vm import JuVM
from restrain_jit.bejulia.jl_init import init
import numpy as np
init()
jit = JuVM.func_info
xs = np.arange(1000)

@jit
def all_add2(lst):
    @select(lst)
    def ret(elt):
        return elt + 2

    return ret

# trigger the JIT compilation
all_add2(xs)

import timeit
from builtins import map

def py_all_add2(lst):
    # according to stackoverflow.com/questions/35215161/,
    # apart from the true vectorizations,
    # 'np.fromiter' is the most efficient way to
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

```