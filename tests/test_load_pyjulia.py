from restrain_jit.bejulia.julia_vm import JuVM
from restrain_jit.bejulia.jl_init import init

init()

jit = JuVM.func_info


@jit
def func1(x):
    for i in range(1000):
        x = x + i
    return x + 1


def func2(x):
    for i in range(1000):
        x += i
    return x + 1


assert func1(100) == func2(100)

print(func1.__jit__)