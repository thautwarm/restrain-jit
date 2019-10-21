from restrain_jit.becy.representations import Repr, Reg
import restrain_jit.becy.stack_vm_instructions as sv
import restrain_jit.becy.phi_vm as phi
import typing as t
from collections import defaultdict
from dataclasses import dataclass

Label = object
Target = Label


class LeftStack:
    name: Label
    objs: t.List[Repr]
    requested: int

    def __init__(self, name, objs, requested=0):
        self.name = name
        self.objs = objs
        self.requested = requested

    def __repr__(self):
        return '{!r}{!r}'.format(self.name, self.objs)


FromLabel = object

From = t.Union[FromLabel, LeftStack]


class HigherOrderStackUsage(Exception):
    pass


class PhiNodeAnalysis:
    current_left_stack: t.Optional[LeftStack]

    # when a block exits, the object lefted on the stack
    left_stacks: t.Dict[Label, LeftStack]

    # indicates the blocks that current block comes from
    come_from: t.Dict[Target, t.Set[From]]

    # indicates the use of stack objects from current block's parent blocks
    pops: t.Dict[Label, t.Dict[str, int]]

    # stores the instruction operands of label.
    phi_dict: t.Dict[Label, t.Dict[object, t.Dict[Reg, Repr]]]

    # is ended in current block
    come_to_end: bool

    def __init__(self, sv_instrs: t.List[sv.A]):
        self.left_stacks = {}
        self.current_left_stack = LeftStack("", [])
        self.come_from = defaultdict(set)
        self.sv_instrs = sv_instrs
        self.pops = defaultdict(dict)
        self.phi_dict = {}
        self.come_to_end = True

    def __getitem__(self, item) -> t.Union[Repr, int]:
        it = self.current_left_stack
        try:
            return it.objs[item]
        except IndexError:
            assert item < 0
            return it.requested - item - len(it.objs)

    def pop(self) -> t.Union[Repr, int]:
        it = self.current_left_stack
        try:
            return it.objs.pop()
        except IndexError:
            it.requested += 1
            return it.requested

    def push(self, r: Repr):
        self.current_left_stack.objs.append(r)

    def check_if_has_entry_label(self):
        #  if the first instruction is a Label
        pass

    def end_block(self, other_block: object = None):
        assert self.current_left_stack
        if other_block:
            self.come_from[other_block].add(self.current_left_stack)

        self.left_stacks[
            self.current_left_stack.name] = self.current_left_stack
        self.come_to_end = True

    def start_block(self, new_block):
        if self.come_to_end:
            self.come_from[new_block].add(self.current_left_stack)
        else:
            self.end_block(new_block)
        self.current_left_stack = LeftStack(new_block, [])
        self.come_to_end = False

    def peek_n(self, n: int, at: From):
        if isinstance(at, LeftStack):
            try:
                return at.objs[-n]
            except IndexError:
                raise HigherOrderStackUsage

        stack = self.left_stacks[at]
        try:
            return stack.objs[-n]
        except IndexError:
            raise HigherOrderStackUsage

    def main(self):
        sv_instrs = self.sv_instrs

        for ass in sv_instrs:
            # print('===', ass, '====', self.left_stacks)
            rhs = ass.rhs
            lhs = ass.lhs
            if not lhs:
                # can be label or terminate instruction
                if isinstance(rhs, sv.Label):
                    self.start_block(rhs.label)
                    full = self.phi_dict[rhs.label] = defaultdict(dict)
                    yield phi.A(None, phi.Label(rhs.label, full))
                    continue
                elif isinstance(rhs, sv.Jmp):
                    self.end_block(rhs.label)
                    yield phi.A(None, phi.Jmp(rhs.label))
                    continue
                elif isinstance(rhs, sv.JmpIf):
                    self.end_block(rhs.label)
                    yield phi.A(None, phi.JmpIf(rhs.label, rhs.cond))
                    continue
                elif isinstance(rhs, sv.JmpIfPush):
                    objs = [*self.current_left_stack.objs, rhs.leave]
                    requested = self.current_left_stack.requested
                    name = self.current_left_stack.name
                    tmp, self.current_left_stack = self.current_left_stack, LeftStack(
                        name, objs, requested)
                    self.end_block(rhs.label)
                    self.current_left_stack = tmp
                    yield phi.A(None, phi.JmpIf(rhs.label, rhs.cond))
                    continue
            if isinstance(rhs, sv.SetLineno):
                yield phi.A(None, phi.SetLineno(rhs.lineno))
            elif isinstance(rhs, sv.Return):
                self.end_block()
                yield phi.A(None, phi.Return(rhs.val))
            elif isinstance(rhs, sv.App):
                yield phi.A(lhs, phi.App(rhs.f, rhs.args))
            elif isinstance(rhs, sv.Ass):
                yield phi.A(lhs, phi.Ass(rhs.reg, rhs.val))
            elif isinstance(rhs, sv.Store):
                yield phi.A(lhs, phi.Store(rhs.reg, rhs.val))
            elif isinstance(rhs, sv.PyGlob):
                yield phi.A(lhs, phi.PyGlob(rhs.qual, rhs.name))
            elif isinstance(rhs, sv.CyGlob):
                yield phi.A(lhs, phi.CyGlob(rhs.qual, rhs.name))
            elif isinstance(rhs, sv.Load):
                yield phi.A(lhs, phi.Load(rhs.reg))
            elif isinstance(rhs, sv.Push):
                self.push(rhs.val)
            elif isinstance(rhs, sv.Peek):
                val = self[-rhs.offset]
                if isinstance(val, Repr):
                    yield phi.A(None, phi.Ass(Reg(lhs), val))
                else:
                    cur_name = self.current_left_stack.name
                    drawback_name = "drawback{}-{}".format(
                        cur_name, val)
                    self.pops[cur_name][drawback_name] = val

                    if lhs is not None:
                        yield phi.A(
                            None, phi.Ass(Reg(lhs), Reg(drawback_name)))
            elif isinstance(rhs, sv.Pop):
                val = self.pop()
                if isinstance(val, Repr):
                    yield phi.A(None, phi.Ass(Reg(lhs), val))
                else:
                    cur_name = self.current_left_stack.name
                    drawback_name = "drawback{}-{}".format(
                        cur_name, val)
                    self.pops[cur_name][drawback_name] = val
                    if lhs is not None:
                        yield phi.A(
                            None, phi.Ass(Reg(lhs), Reg(drawback_name)))

        pops = self.pops
        come_from = self.come_from
        fulls = self.phi_dict
        for label, requires in pops.items():
            phi_dispatch_cases = fulls[label]
            for (reg_name, peek_n) in requires.items():
                for can_from in come_from[label]:
                    can_from_label = can_from.name if isinstance(
                        can_from, LeftStack) else can_from
                    assert isinstance(peek_n, int)
                    r = self.peek_n(peek_n, at=can_from)
                    label_phi = phi_dispatch_cases[can_from_label]
                    label_phi[Reg(reg_name)] = r
