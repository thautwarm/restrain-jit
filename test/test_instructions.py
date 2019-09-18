from restrain_jit.bejulia.julia_vm import JuVM, UnwindBlock, App, Repr, Reg, Const
from restrain_jit.jit_info import PyCodeInfo

jit = JuVM.func_info


def show_instrs(instrs, indent=''):

    for a in instrs:
        k = a.lhs
        v = a.rhs
        if k is not None:
            print(indent + k, '=', end=' ')
        else:
            print(indent, end='')
        next_indent = indent + '        '
        if isinstance(v, UnwindBlock):
            print()
            show_instrs(v.instrs, next_indent)
        elif isinstance(v, App):
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


@jit
def func1(x):

    @foreach(prange(1000))
    def apply(e):
        do_some(e)


show_instrs(func1.__func_info__.r_codeinfo.instrs)
