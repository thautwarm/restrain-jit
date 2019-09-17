import bytecode as bc
from restrain_jit.bejulia.julia_vm import JuVM
from restrain_jit.vm.am import run_machine
from restrain_jit.bejulia.jl_init import init

init()

jit = JuVM.func_info

@jit
def func(x):
    for i in range(1000):
        print(i)
    return x + 1


code = bc.Bytecode.from_code(func.__code__)
cfg = bc.ControlFlowGraph.from_bytecode(code)
jvm = JuVM.empty()
run_machine(abs_i_cfg(cfg), jvm)

instrs = jvm.instrs
jvm.pass_push_pop_inline(instrs)

aware = init()
aware(instrs)

# jl.eval("1")
