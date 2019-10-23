import sys

from restrain_jit.becython.cython_vm import CyVM, App, Repr, Reg, Const, Options
from restrain_jit.becython.tools import show_instrs
from restrain_jit.becython.cy_codegen import CodeEmitter
jit = CyVM.func_info

# DEBUG['stack-vm'] = True
# Options['log-phi'] = True


@jit
def f(x, y):
    s = x
    for i in y:
        s += i
    return s


io = sys.stdout
instrs = f.__func_info__.r_codeinfo.instrs
CodeEmitter(io).emit(instrs)

