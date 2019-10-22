from restrain_jit.becython.cython_vm import CyVM, App, Repr, Reg, Const, DEBUG
from restrain_jit.becython.tools import show_instrs
jit = CyVM.func_info

# DEBUG['stack-vm'] = True
# DEBUG['phi-elim'] = True


@jit
def f(x, y):
    for i in y:
        print(x + i)



