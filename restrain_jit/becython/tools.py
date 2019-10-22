from restrain_jit.becython import stack_vm_instructions as sv
from restrain_jit.becython import phi_vm as phi
from restrain_jit.becython import mono_vm as mono

from restrain_jit.jit_info import PyCodeInfo

sv_jumps = (sv.JmpIfPush, sv.JmpIf, sv.Jmp)


def show_mono_instrs(instrs, indent=''):
    for v in instrs:
        k = getattr(v, 'target', None)
        if k is not None:
            print(indent + k, '=', end=' ')
        else:
            print(indent, end='')
        next_indent = indent + '        '
        if isinstance(v, mono.App):
            print('call', v.f)
            for each in v.args:
                if isinstance(each, mono.Const) and isinstance(
                        each.val, PyCodeInfo):
                    print(next_indent, "function", each.val.name)
                    show_instrs(each.val.instrs,
                                next_indent + "         ")
                else:
                    print(next_indent, each, sep='')
        elif isinstance(v, mono.Label):
            print(indent, 'label ', v.label, ':', sep='')
        else:
            print(v)


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
                    print(next_indent, each, sep='')
        elif isinstance(v, phi.Label):
            print(indent, 'label ', v.label, ':', sep='')
            for label_name, values in v.phi.items():
                print(indent + '  ', label_name, ': ', sep='', end='')
                for reg_name, v in values.items():
                    print('{} = {}'.format(reg_name.n, v), end=', ')
                if values:
                    print()
        else:
            print(v)
