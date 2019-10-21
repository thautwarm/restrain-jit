from restrain_jit.becy.cython_vm import CyVM, App, Repr, Reg, Const
from restrain_jit.becy.tools import show_instrs
jit = CyVM.func_info


@jit
def f(x, y):
    for i in y:
        print(x + i)

show_instrs(f.__func_info__.r_codeinfo.instrs)