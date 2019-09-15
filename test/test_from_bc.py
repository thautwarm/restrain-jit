from restrain_jit.bejulia.julia_vm import JuVM
from restrain_jit.vm.am import run_machine
from restrain_jit.ir.from_bc import abs_i_cfg
import bytecode as bc
import typing as t


class S(dict):

    def __missing__(self, key):
        v = self[key] = len(self)
        return v


def show_block(x):
    s = S()
    for ins in x:
        print('===== block ', s[id(ins)])
        for j in ins:
            if isinstance(j.arg, bc.BasicBlock):
                print(j.name, ' -> block', s[id(j.arg)])
            else:
                print(j)


jvm = JuVM([], [], set(), set())


def f(x):
    for each in x:
        a = each + 1
        if a < 2:
            k(a).d()


code = bc.Bytecode.from_code(f.__code__)
cfg = bc.ControlFlowGraph.from_bytecode(code)

show_block(cfg)
block1: t.List[bc.Instr] = list(cfg[0])

run_machine(abs_i_cfg(cfg), jvm)
jvm.pass_push_pop_inline()
print('=============')

for k, v in jvm.instrs:
    if k is None:
        print(v)
    else:
        print(k, '=', v)
