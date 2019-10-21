from restrain_jit.becy import stack_vm_instructions as sv
from restrain_jit.becy import phi_vm as phi

from restrain_jit.jit_info import PyCodeInfo

sv_jumps = (sv.JmpIfPush, sv.JmpIf, sv.Jmp)


def show_instrs(instrs, indent=''):
    for a in instrs:
        k = a.lhs
        v = a.rhs
        if k is not None:
            print(indent + k, '=', end=' ')
        else:
            print(indent, end='')
        next_indent = indent + '        '
        if isinstance(v, (sv.App, phi.App)):
            print('call', v.f)
            for each in v.args:
                if isinstance(each,
                              (sv.Const, phi.Const)) and isinstance(
                                  each.val, PyCodeInfo):
                    print(next_indent, "function", each.val.name)
                    show_instrs(each.val.instrs,
                                next_indent + "         ")
                else:
                    print(next_indent, each)
        elif isinstance(v, phi.Label):
            print(indent, 'label ', v.label, ':', sep='')
            for from_label, values in v.phi.items():
                print(indent + '  ', ' from ', from_label, sep='')
                for k, v in values.items():
                    print(next_indent, k.n, ' = ', v, sep='')

            print(next_indent, )
        else:
            print(v)
