"""
Convert stack-vm instructions to reg vm with Phi-node constructs.
This file is preserved for prospective Cython-like backends with Phi-node constructs.
Say, LLVM IR has Phi-nodes, as well as Julia IR
"""
from restrain_jit.becython.representations import Repr, Reg
import restrain_jit.becython.stack_vm_instructions as sv
import restrain_jit.becython.phi_vm as phi

import typing as t
from collections import defaultdict, OrderedDict

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


def pop_or_peek(self, lhs, val):
    if isinstance(val, Repr):
        if lhs is not None:
            self += phi.Ass(lhs, val)

    elif lhs is not None:
        cur_name = self.current_left_stack.name
        drawback_name = self.drawback_name(cur_name, val)
        self.pops[cur_name] = max(self.pops[cur_name], val)
        self += phi.Ass(lhs, Reg(drawback_name))


class Phi:
    current_left_stack: t.Optional[LeftStack]

    # when a block exits, the object lefted on the stack
    left_stacks: t.Dict[Label, LeftStack]

    # indicates the blocks that current block comes from
    come_from: t.Dict[Target, t.Set[From]]

    # indicates the use of stack objects from current block's parent blocks
    pops: t.Dict[Label, int]

    # stores the instruction operands of label.
    phi_dict: t.Dict[Label, t.Dict[Label, t.Dict[str, Repr]]]

    # is ended in current block
    come_to_end: bool

    def drawback_name(self, from_label, drawback_n: int):
        return 'drawback_{}{}'.format(from_label, drawback_n)

    def __init__(self, sv_instrs: t.List[sv.A]):
        self.left_stacks = {}
        self.current_left_stack = LeftStack("", [])
        self.come_from = defaultdict(set)
        self.sv_instrs = sv_instrs
        self.pops = defaultdict(lambda: 0)
        self.phi_dict = {}
        self.come_to_end = True
        self.elim_phi = True

        self.blocks = OrderedDict()
        self.block = []

    def __iadd__(self, other):
        self.block.append(other)
        return self

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

    def end_block(self, other_label_addr: object = None):
        if self.come_to_end:
            return
        assert self.current_left_stack
        if other_label_addr:
            self.come_from[other_label_addr].add(
                self.current_left_stack)
        self.block = []
        self.come_to_end = True

    def start_block(self, new_label_addr):
        if self.come_to_end:
            self.come_from[new_label_addr].add(self.current_left_stack)
        else:
            self.end_block(new_label_addr)
        self.left_stacks[
            new_label_addr] = self.current_left_stack = LeftStack(
                new_label_addr, [])
        self.blocks[self.current_left_stack.name] = self.block
        self.come_to_end = False

    def peek_n(self, n: int, at: From):
        if not isinstance(at, LeftStack):
            at = self.left_stacks[at]

        try:
            return at.objs[-n]
        except IndexError:
            come_from = self.come_from[at.name]
            if len(come_from) is 1:
                come_from = next(iter(come_from))
                n = n - len(at.objs) + self.pops[at.name]
                return self.peek_n(n, come_from)
            raise HigherOrderStackUsage


def main(sv_instrs):
    self = Phi(sv_instrs)
    sv_instrs = self.sv_instrs

    for ass in sv_instrs:

        rhs = ass.rhs
        lhs = ass.lhs
        if not lhs:
            # can be label or terminate instruction
            if isinstance(rhs, sv.Label):
                self.start_block(rhs.label)
                full = self.phi_dict[rhs.label] = defaultdict(dict)
                self += phi.BeginBlock(rhs.label, full)
                continue
            elif isinstance(rhs, sv.Jmp):
                self.end_block(rhs.label)
                self += phi.Jmp(rhs.label)
                continue
            elif isinstance(rhs, sv.JmpIf):
                self.end_block(rhs.label)
                self += phi.JmpIf(rhs.label, rhs.cond)
                continue
            elif isinstance(rhs, sv.JmpIfPush):
                objs = [*self.current_left_stack.objs, rhs.leave]
                requested = self.current_left_stack.requested
                name = self.current_left_stack.name
                tmp, self.current_left_stack = self.current_left_stack, LeftStack(
                    name, objs, requested)
                self.end_block(rhs.label)
                self.current_left_stack = tmp
                self += phi.JmpIf(rhs.label, rhs.cond)
                continue
        if isinstance(rhs, sv.SetLineno):
            self += phi.SetLineno(rhs.lineno)

        elif isinstance(rhs, sv.Return):
            self += phi.Return(rhs.val)
            self.end_block()

        elif isinstance(rhs, sv.App):
            self += phi.App(lhs, rhs.f, rhs.args)

        elif isinstance(rhs, sv.Ass):
            self += phi.Ass(rhs.reg.n, rhs.val)
            if lhs:
                self += phi.Ass(lhs, rhs.val)

        elif isinstance(rhs, sv.Store):
            assert not lhs
            self += phi.Store(rhs.reg.n, rhs.val)

        elif isinstance(rhs, sv.PyGlob):
            self += phi.PyGlob(lhs, rhs.qual, rhs.name)

        elif isinstance(rhs, sv.CyGlob):
            self += phi.CyGlob(lhs, rhs.qual, rhs.name)

        elif isinstance(rhs, sv.Load):
            if lhs:
                self += phi.Load(lhs, rhs.reg)

        elif isinstance(rhs, sv.Push):
            self.push(rhs.val)
        else:
            if isinstance(rhs, sv.Peek):
                val = self[-rhs.offset]

            elif isinstance(rhs, sv.Pop):
                val = self.pop()
            else:
                raise NotImplementedError(rhs)
            pop_or_peek(self, lhs, val)

    self.end_block()

    pops = self.pops
    come_from = self.come_from
    fulls = self.phi_dict

    for label, max_required in pops.items():
        phi_dispatch_cases = fulls[label]
        for peek_n in range(1, max_required + 1):
            reg_name = self.drawback_name(label, peek_n)
            for can_from in come_from[label]:
                can_from_label = can_from.name if isinstance(
                    can_from, LeftStack) else can_from
                assert isinstance(peek_n, int)
                r = self.peek_n(peek_n, at=can_from)
                reg_dispatch_cases = phi_dispatch_cases[can_from_label]
                reg_dispatch_cases[reg_name] = r

    for label, instrs in self.blocks.items():
        yield from instrs
        yield phi.EndBlock()
