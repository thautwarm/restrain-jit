from restrain_jit.becy.cython_vm import CyVM, App, Repr, Reg, Const, DEBUG
from restrain_jit.becy.tools import show_instrs
jit = CyVM.func_info

DEBUG['phi'] = True


@jit
def f(x, y):
    for i in y:
        print(x + i)
