from restrain_jit.bejulia.julia_vm import JuVM, UnwindBlock
from restrain_jit.vm.am import run_machine
from restrain_jit.ir.from_bc import abs_i_cfg
import bytecode as bc
import typing as t


class S(dict):

    def __missing__(self, key):
        v = self[key] = len(self)
        return v


def show_block(x):
    s = S()
    for ins in x:
        print('===== block ', s[id(ins)])
        for j in ins:
            if isinstance(j.arg, bc.BasicBlock):
                print(j.name, ' -> block', s[id(j.arg)])
            else:
                print(j)


def f1(x):
    with x:
        for each in x:
            a = each + 1
            if a < 2:
                k(a).d()


def f2():
    try:
        1 / 0
    except ZeroDivisionError:
        raise Exception
    except Exception:
        print(2)
    finally:
        print(3)


c = JuVM.code_info(f2.__code__)


def show(instrs, indent=''):
    for k, v in instrs:
        if k is not None:
            print(indent + k, '=', end='')
        else:
            print(indent, end='')
        if isinstance(v, UnwindBlock):
            next_indent = indent + '    '
            print()
            show(v.instrs, next_indent)
        else:
            print(v)


show(c.instrs)
