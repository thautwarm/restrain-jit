from restrain_jit.becython.phi_elim import PhiElimViaMove
from restrain_jit.becython.stack_vm_instructions import *
from restrain_jit.becython.cy_codegen import CodeEmitter
from restrain_jit.becython.tools import show_instrs
import sys
instrs = [
    A(None, Label(label=0)),
    A(None, Push(Reg("x0"))),
    A(None, JmpIfPush(2, Reg("x0"), Reg("x0"))),
    A(None, Label(label=1)),
    A(None, Push(Reg("x1"))),
    A(None, Label(label=2)),
    A("c", Pop()),
    A(None, Return(Reg("c")))
]

instrs = PhiElimViaMove(instrs).main()
io = sys.stdout
CodeEmitter(io).emit(instrs)