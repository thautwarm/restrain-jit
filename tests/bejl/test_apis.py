from restrain_jit.bejulia.jl_init import init
from restrain_jit.bejulia.julia_vm import JuVM

init()

jit = JuVM.func_info


@jit
def test_bool(value: bool):
    return not value


print(test_bool(True))
