from restrain_jit.bejulia.functional import foreach, select, J

from restrain_jit.bejulia.pragmas import const
from restrain_jit.bejulia.julia_vm import JuVM
from restrain_jit.bejulia.jl_init import init

init()
jit = JuVM.func_info

a = J @ {1, 2, 3}

@jit
def f(x):
    # x.append(1)
    print(x)


print(f(a))
