"""
Convert stack-vm instructions to reg vm with Phi-node constructs,
then using move-like semantics to eliminate Phi-nodes.
"""
from restrain_jit.becython.representations import Repr, Reg
import restrain_jit.becython.stack_vm_instructions as sv
import restrain_jit.becython.mono_vm as mono

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


def pop_or_peek(self, lhs, rhs, val):
    if isinstance(val, Repr):
        if lhs is not None:
            # yield phi.A(None, phi.Ass(Reg(lhs), val))
            self.add_mono_instr(mono.Ass(lhs, val))

    else:
        cur_name = self.current_left_stack.name
        drawback_name = self.drawback_name(cur_name, val)
        # FIXME: should be max(val, ...)
        self.pops[cur_name] = val
        if lhs is not None:
            # yield phi.A(None, phi.Ass(Reg(lhs), Reg(drawback_name)))
            self.add_mono_instr(mono.Ass(lhs, Reg(drawback_name)))


class PhiElimViaMove:
    current_left_stack: t.Optional[LeftStack]

    # when a block exits, the object lefted on the stack
    left_stacks: t.Dict[Label, LeftStack]

    # indicates the blocks that current block comes from
    come_from: t.Dict[Target, t.Set[From]]

    # indicates the use of stack objects from current block's parent blocks
    pops: t.Dict[Label, int]

    # is ended in current block
    come_to_end: bool

    blocks: t.Dict[Label, t.List[mono.Instr]]

    @staticmethod
    def drawback_name(from_label, drawback_n: int):
        return 'drawback_{}{}'.format(from_label, drawback_n)

    def __init__(self, sv_instrs: t.List[sv.A], elim_phi=True):
        self.left_stacks = {}
        self.current_left_stack = LeftStack("", [])
        self.come_from = defaultdict(set)

        self.sv_instrs = sv_instrs
        self.pops = {}
        self.phi_dict = {}
        self.come_to_end = True
        self.elim_phi = True

        self.blocks = OrderedDict()
        self.current_block = []

    def add_mono_instr(self, instr: mono.Instr):
        self.current_block.append(instr)

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
        self.blocks[self.current_left_stack.name] = self.current_block
        self.current_block = []
        self.come_to_end = True

    def start_block(self, new_label_addr):
        if self.come_to_end:
            self.come_from[new_label_addr].add(self.current_left_stack)
        else:
            self.end_block(new_label_addr)
        left_stack = LeftStack(new_label_addr, [])
        self.left_stacks[
            new_label_addr] = self.current_left_stack = left_stack
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
    self = PhiElimViaMove(sv_instrs)

    for ass in sv_instrs:

        rhs = ass.rhs
        lhs = ass.lhs
        if not lhs:
            # can be label or terminate instruction
            if isinstance(rhs, sv.Label):
                self.start_block(rhs.label)
                self.phi_dict[rhs.label] = defaultdict(dict)
                # yield phi.A(None, phi.Label(rhs.label, full))
                continue
            elif isinstance(rhs, sv.Jmp):
                self.add_mono_instr(mono.SetCont(rhs.label))
                self.end_block(rhs.label)
                # yield phi.A(None, phi.Jmp(rhs.label))
                continue
            elif isinstance(rhs, sv.JmpIf):
                self.add_mono_instr(mono.SetContIf(rhs.label, rhs.cond))
                self.end_block(rhs.label)
                continue
            elif isinstance(rhs, sv.JmpIfPush):
                objs = [*self.current_left_stack.objs, rhs.leave]
                requested = self.current_left_stack.requested
                name = self.current_left_stack.name
                tmp, self.current_left_stack = self.current_left_stack, LeftStack(
                    name, objs, requested)
                self.add_mono_instr(mono.SetContIf(rhs.label, rhs.cond))

                self.end_block(rhs.label)
                self.current_left_stack = tmp
                # yield phi.A(None, phi.JmpIf(rhs.label, rhs.cond))
                continue
        if isinstance(rhs, sv.SetLineno):
            # yield phi.A(None, phi.SetLineno(rhs.lineno))
            self.add_mono_instr(mono.SetLineno(rhs.lineno))
        elif isinstance(rhs, sv.Return):
            self.add_mono_instr(mono.Return(rhs.val))
            self.end_block()
            # yield phi.A(None, phi.Return(rhs.val))
        elif isinstance(rhs, sv.App):
            # yield phi.A(lhs, phi.App(rhs.f, rhs.args))
            self.add_mono_instr(mono.App(lhs, rhs.f, rhs.args))
        elif isinstance(rhs, sv.Ass):
            # yield phi.A(lhs, phi.Ass(rhs.reg, rhs.val))
            self.add_mono_instr(mono.Ass(rhs.reg.n, rhs.val))
            if lhs is not None:
                self.add_mono_instr(mono.Ass(lhs, rhs.reg))
        elif isinstance(rhs, sv.Store):
            # yield phi.A(lhs, phi.Store(rhs.reg, rhs.val))
            self.add_mono_instr(mono.Store(rhs.reg.n, rhs.val))
            if lhs is not None:
                self.add_mono_instr(mono.Store(lhs, rhs.reg))

        elif isinstance(rhs, sv.PyGlob):
            # yield phi.A(lhs, phi.PyGlob(rhs.qual, rhs.name))
            self.add_mono_instr(mono.PyGlob(lhs, rhs.qual, rhs.name))

        elif isinstance(rhs, sv.CyGlob):
            # yield phi.A(lhs, phi.CyGlob(rhs.qual, rhs.name))
            self.add_mono_instr(mono.CyGlob(lhs, rhs.qual, rhs.name))

        elif isinstance(rhs, sv.Load):
            # yield phi.A(lhs, phi.Load(rhs.reg))
            self.add_mono_instr(mono.Load(lhs, rhs.reg))

        elif isinstance(rhs, sv.Push):
            self.push(rhs.val)
        else:
            if isinstance(rhs, sv.Peek):
                val = self[-rhs.offset]

            elif isinstance(rhs, sv.Pop):
                val = self.pop()
            else:
                raise NotImplementedError(rhs)
            pop_or_peek(self, lhs, rhs, val)

    self.end_block()

    pops = self.pops
    come_from = self.come_from

    for label, max_required in pops.items():
        for peek_n in range(1, max_required + 1):
            reg_name = self.drawback_name(label, peek_n)
            for can_from in come_from[label]:
                can_from_label = can_from.name if isinstance(
                    can_from, LeftStack) else can_from
                assert isinstance(peek_n, int)
                r = self.peek_n(peek_n, at=can_from)
                # use move to remove phi nodes
                self.blocks[can_from_label].append(
                    mono.MoveOrAss(reg_name, r))

    for label, instrs in self.blocks.items():
        yield mono.BeginBlock(label)
        yield from instrs
        yield mono.EndBlock()
