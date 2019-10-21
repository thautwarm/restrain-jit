from restrain_jit.becy.stack_vm_instructions import App, Const, JmpIf, JmpIfPush, Jmp
from restrain_jit.jit_info import PyCodeInfo

jumps = (JmpIfPush, JmpIf, Jmp)


def show_instrs(instrs, indent=''):
    for a in instrs:
        k = a.lhs
        v = a.rhs
        if k is not None:
            print(indent + k, '=', end=' ')
        else:
            print(indent, end='')
        next_indent = indent + '        '
        if isinstance(v, App):
            print('call', v.f)
            for each in v.args:
                if isinstance(each, Const) and isinstance(
                        each.val, PyCodeInfo):
                    print(next_indent, "function", each.val.name)
                    show_instrs(each.val.instrs,
                                next_indent + "         ")
                else:
                    print(next_indent, each)

        else:
            print(v)
