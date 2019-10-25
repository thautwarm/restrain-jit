from restrain_jit.becython import stack_vm_instructions as sv
from restrain_jit.becython import phi_vm as phi
from restrain_jit.becython import mono_vm as mono
from restrain_jit.jit_info import PyCodeInfo
import typing as t
sv_jumps = (sv.JmpIfPush, sv.JmpIf, sv.Jmp)


def show_mono_instrs(instrs: t.List[mono.Instr], indent=''):
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
        elif isinstance(v, mono.BeginBlock):
            print('label {}'.format(v.label).center(20, '='))
        elif isinstance(v, mono.EndBlock):
            print('end'.center(20, '='))
        else:
            print(v)


def show_stack_instrs(instrs: t.List[sv.A], indent=''):
    for a in instrs:
        k = a.lhs
        v = a.rhs
        if k is not None:
            print(indent + k, '=', end=' ')
        else:
            print(indent, end='')
        next_indent = indent + '        '
        if isinstance(v, sv.App):
            print('call', v.f)
            for each in v.args:
                if isinstance(each, sv.Const) and isinstance(
                        each.val, PyCodeInfo):
                    print(next_indent, "function", each.val.name)
                    show_instrs(each.val.instrs,
                                next_indent + "         ")
                else:
                    print(next_indent, each, sep='')
        else:
            print(v)


def show_phi_instrs(instrs: t.List[phi.Instr], indent=''):
    for a in instrs:
        k = getattr(a, 'target', None)
        if k is not None:
            print(indent + k, '=', end=' ')
        else:
            print(indent, end='')
        next_indent = indent + '        '
        if isinstance(a, phi.App):
            print('call', a.f)
            for each in a.args:
                if isinstance(each, phi.Const) and isinstance(
                        each.val, PyCodeInfo):
                    print(next_indent, "function", each.val.name)
                    show_instrs(each.val.instrs,
                                next_indent + "         ")
                else:
                    print(next_indent, each, sep='')
        elif isinstance(a, phi.BeginBlock):
            print(indent, 'label ', a.label, ':', sep='')
            for label_name, values in a.phi.items():
                print(indent + '  ', label_name, ': ', sep='', end='')
                for reg_name, a in values.items():
                    print('{} = {}'.format(reg_name, a), end=', ')
                if values:
                    print()
        else:
            print(a)


def show_instrs(instrs, t=None):
    if t is None:
        t = type(instrs[0])
    if issubclass(t, mono.Instr):
        show_mono_instrs(instrs)
        return
    elif issubclass(t, sv.A):
        show_stack_instrs(instrs)
        return
    elif issubclass(t, phi.Instr):
        show_phi_instrs(instrs)
    else:
        raise TypeError("Instructions is a List of {}".format(t))
