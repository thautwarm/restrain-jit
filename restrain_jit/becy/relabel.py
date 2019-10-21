import restrain_jit.becy.stack_vm_instructions as sv
from restrain_jit.becy.tools import sv_jumps
import typing as t


def apply(instrs: t.List[sv.A]):
    target_labels = {}
    # TODO: using "whether in used_labels" to decide
    #       "whether to codegen as a subroutine".
    used_labels = set()
    for ass in instrs:
        if ass.lhs:
            # cannot be jump or label
            continue
        rhs = ass.rhs
        if isinstance(rhs, sv.Label):
            target_labels[rhs.label] = len(target_labels)
        elif isinstance(rhs, sv_jumps):
            used_labels.add(rhs.label)

    for ass in instrs:
        if not ass.lhs:
            rhs = ass.rhs
            if isinstance(rhs, sv.Label):
                if rhs.label in target_labels:
                    yield sv.A(None, sv.Label(target_labels[rhs.label]))
                continue
            elif isinstance(rhs, sv.JmpIf):
                yield sv.A(None,
                           sv.JmpIf(target_labels[rhs.label], rhs.cond))
                continue
            elif isinstance(rhs, sv.JmpIfPush):
                yield sv.A(
                    None,
                    sv.JmpIfPush(target_labels[rhs.label], rhs.cond,
                                 rhs.leave))
                continue
            elif isinstance(rhs, sv.Jmp):
                yield sv.A(None, sv.Jmp(target_labels[rhs.label]))
                continue
        yield ass
