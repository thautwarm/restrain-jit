from restrain_jit.becy.phi_node_analysis import PhiNodeAnalysis
from restrain_jit.becy.stack_vm_instructions import *
from restrain_jit.becy.tools import show_instrs

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


show_instrs(list(PhiNodeAnalysis(instrs).main()))