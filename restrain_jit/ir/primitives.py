from restrain_jit.ir import instructions as Instr, representations as Repr
from restrain_jit.ir import instrnames as InstrNames


def add_instr(instr: Instr.Instr):
    raise NotImplemented


def pop():
    raise NotImplemented


def push(r: Repr.Repr):
    raise NotImplemented


def tmp(instr: Instr.Instr):
    raise NotImplemented
