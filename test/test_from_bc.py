from restrain_jit.vm.julia_vm import JuVM
from restrain_jit.vm.am import run_machine, Symbol
from restrain_jit.ir.from_bc import abs_i
from restrain_jit.ir.instructions import *
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


def g(block):
    for e in block:
        yield from abs_i(e)


jvm = JuVM([], [], set(), set())


def f(x):
    a = x + 1
    return k(a).d


code = bc.Bytecode.from_code(f.__code__)
cfg = bc.ControlFlowGraph.from_bytecode(code)
show_block(cfg)
block1: t.List[bc.Instr] = list(cfg[0])

run_machine(g(block1), jvm)
jvm.pass_push_pop_inline()
print('=============')

for k, v in jvm.instrs:
    if k is None:
        print(v)
    else:
        print(k, '=', v)

assert jvm.instrs == [
    ('tmp-0', PyGlob(qual='RestrainJIT', name='py_add')),
    ('tmp-1', App(f=Reg(n='tmp-0'), args=[Reg(n='x'),
                                          Const(val=1)])),
    (None, Ass(reg=Reg(n='a'), val=Reg(n='tmp-1'))),
    ('tmp-2', PyGlob(qual='', name='k')),
    ('tmp-3', App(f=Reg(n='tmp-2'), args=[Reg(n='a')])),
    ('tmp-4', PyGlob(qual='RestrainJIT', name='py_get_attr')),
    ('tmp-5',
     App(f=Reg(n='tmp-4'),
         args=[Reg(n='tmp-3'), Const(val=Symbol(s='d'))])),
    (None, Return(val=Reg(n='tmp-5')))
]
