from restrain_jit.bejulia.julia_vm import JuVM, UnwindBlock, App, Repr, Reg, Const
from restrain_jit.jit_info import PyCodeInfo
from restrain_jit.bejulia.tools import show_instrs

jit = JuVM.func_info


@jit
def f(x, y):
    pass


show_instrs(f.__func_info__.r_codeinfo.instrs)

#
# @jit
# def func1(x):
#     x[:2] = 1
#
#
# show_instrs(func1.__func_info__.r_codeinfo.instrs)
