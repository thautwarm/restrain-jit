from restrain_jit.bejulia.functional import foreach, select, J
from restrain_jit.bejulia.tools import show_instrs
from restrain_jit.bejulia.pragmas import const
from restrain_jit.bejulia.julia_vm import JuVM
from restrain_jit.bejulia.jl_init import init
#
import numpy as np
init()
jit = JuVM.func_info

a = J @ [1, 2, 3]


@jit
def test_append(x):
    x.append(1)
    return x


# show_instrs(f.__func_info__.r_codeinfo.instrs)
print(test_append(a) == np.array([1, 2, 3, 1]))


@jit
def test_repeat_append_jit():
    x = [1]
    x.pop()

    for i in range(10000):
        x.append(i)
    return x


@jit
def test_repeat_append_jit_foreach():
    x = [1]
    x.pop()

    @foreach(range(10000))
    def each(e):
        x.append(e)

    return x


def test_repeat_append_nojit():
    x = []
    for i in range(100000):
        x.append(i)
    return x


# print(test_repeat_append_jit())

# print(test_repeat_append_jit_foreach())
#
# for e in (test_repeat_append_jit_foreach.__func_info__.r_codeinfo.instrs):
#     print(e)
# show_instrs(test_repeat_append_jit_foreach.__func_info__.r_codeinfo.instrs)
#
# %timeit test_repeat_append_jit()
# %timeit test_repeat_append_nojit()
# %timeit test_repeat_append_jit_foreach()

from julia import Main

tt = Main.eval("""
function tt()
    x = []
    for i in 0:9999
        push!(x, i)
    end
    x
end
""")
tt()

import timeit

print(timeit.timeit("tt()", globals=dict(tt=tt), number=1000))
print(timeit.timeit(
    "tt()", globals=dict(tt=test_repeat_append_nojit), number=1000))
