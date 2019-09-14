from dataclasses import dataclass
import bytecode as bc
import typing as t
from bytecode import Bytecode
from restrain_jit.ir import instructions as Instr, representations as Repr
from restrain_jit.ir import instrnames as InstrNames
from restrain_jit.ir import primitives as Prim
from restrain_jit.ir import py_apis as RT


@dataclass
class VMFunc:
    # stack
    st: t.List[Repr.Repr]
    # instructions
    instrs: t.List[Instr.Instr]

    # allocated temporary
    used: t.Set[str]
    unsed: t.Set[str]
    blocks: t.List[str]


def label_to_name(label: t.Union[bc.Label, bc.BasicBlock]):
    return f"repy {id(label)}"


def is_pushing_block(b: bc.Instr):
    return b.name in (InstrNames.SETUP_EXCEPT, InstrNames.SETUP_FINALLY,
                      InstrNames.SETUP_FINALLY, InstrNames.SETUP_WITH)


def is_poping_block(b: bc.Instr):
    return b.name in (InstrNames.POP_BLOCK, InstrNames.POP_EXCEPT,
                      InstrNames.END_FINALLY)


def abs_i(b: t.Union[bc.Instr, bc.Label]):
    if isinstance(b, bc.Label):
        yield Prim.add_instr(Instr.Label(label_to_name(b)))
    elif b.has_jump():
        yield from abs_i_jump(b)
    elif b.name.startswith('UNARY'):
        yield from abs_i_unary(b)

    elif b.name.startswith('BINARY'):
        yield from abs_i_binary(b)
    elif b.name.startswith('INPLACE'):
        yield from abs_i_inplace_binary(b)
    elif b.name == InstrNames.ROT_TWO:
        a1 = yield Prim.pop()
        a2 = yield Prim.pop()
        yield Prim.push(a2)
        yield Prim.push(a1)
    elif b.name == InstrNames.ROT_THREE:
        a1 = yield Prim.pop()
        a2 = yield Prim.pop()
        a3 = yield Prim.pop()
        yield Prim.push(a3)
        yield Prim.push(a1)
        yield Prim.push(a2)
    elif b.name == InstrNames.NOP:
        pass
    elif b.name == InstrNames.DUP_TOP:
        a = yield Prim.pop()
        yield Prim.push(a)
        yield Prim.push(a)
    elif b.name == InstrNames.DUP_TOP_TWO:
        a = yield Prim.pop()
        yield Prim.push(a)
        yield Prim.push(a)
        yield Prim.push(a)

    elif b.name == InstrNames.GET_ITER:
        a = yield Prim.pop()
        a = yield from RT.py_iter(a)
        yield Prim.push(a)

    elif b.name == InstrNames.GET_YIELD_FROM_ITER:
        a = yield Prim.pop()
        a = yield from RT.py_iter(a)
        yield Prim.push(a)
    elif b.name == InstrNames.STORE_SUBSCR:
        tos = yield Prim.pop()
        tos1 = yield Prim.pop()
        tos2 = yield Prim.pop()
        yield from RT.py_setitem(tos1, tos, tos2)
    elif b.name == InstrNames.DELETE_SUBSCR:
        tos = yield Prim.pop()
        tos1 = yield Prim.pop()
        yield from RT.py_delitem(tos1, tos)
    elif b.name == InstrNames.PRINT_EXPR:
        tos = yield Prim.pop()
        yield from RT.py_printexpr(tos)
    elif b.name == InstrNames.SET_ADD:
        tos = yield Prim.pop()
        subj = yield Prim.tmp(Instr.Peek(b.arg))
        yield from RT.py_set_add(subj, tos)
    elif b.name == InstrNames.LIST_APPEND:
        tos = yield Prim.pop()
        subj = yield Prim.tmp(Instr.Peek(b.arg))
        yield from RT.py_list_append(subj, tos)
    elif b.name == InstrNames.MAP_ADD:
        tos = yield Prim.pop()
        tos1 = yield Prim.pop()
        subj = yield Prim.tmp(Instr.Peek(b.arg))
        yield from RT.py_map_add(subj, tos, tos1)
    elif b.name == InstrNames.RETURN_VALUE:
        yield Prim.add_instr(Instr.Return())
    elif b.name == InstrNames.YIELD_VALUE:
        yield Prim.add_instr(Instr.Yield())
    elif b.name == InstrNames.YIELD_FROM:
        yield Prim.add_instr(Instr.YieldFrom())
    elif b.name == InstrNames.STORE_NAME:
        assert isinstance(b.arg, str)
        yield Prim.add_instr(Instr.Ass(b.arg, Instr.VarScope.Unknown))
    elif b.name == InstrNames.DELETE_NAME:
        pass
    elif b.name == InstrNames.UNPACK_SEQUENCE:
        val = yield Prim.pop()
        val = yield from RT.py_to_tuple(val)
        for idx in range(b.arg):
            a = yield from RT.py_subscr(val, idx)
            yield Prim.push(a)
    elif b.name == InstrNames.UNPACK_EX:
        val = yield Prim.pop()
        val = yield from RT.py_to_tuple(val)
        n = yield from RT.py_len(val)
        tail = b.arg // 256
        init = b.arg % 256
        start_idx = None
        for start_idx in range(init):
            a = yield from RT.py_subscr(val, start_idx)
            yield Prim.push(a)

        start_idx = Repr.Const(start_idx)
        end_idx = yield from RT.py_sub(n, Repr.Const(tail))
        a = yield from RT.py_build_slice(start_idx, Repr.Const(1), end_idx)
        yield Prim.push(a)

        for end_idx in range(init):
            end_idx = yield from RT.py_sub(n, Repr.Const(end_idx + 1))
            a = yield from RT.py_subscr(val, end_idx)
            yield Prim.push(a)

    elif b.name == InstrNames.FORMAT_VALUE:
        a = yield Prim.pop()
        if b.arg & 0x03 == 0x00:
            a = yield from RT.py_format(a)
        elif b.arg & 0x03 == 0x01:
            a = yield from RT.py_to_str(a)
            a = yield from RT.py_format(a)
        elif b.arg & 0x03 == 0x02:
            a = yield from RT.py_to_repr(a)
            a = yield from RT.py_format(a)
        elif b.arg & 0x03 == 0x03:
            a = yield from RT.py_to_ascii(a)
            a = yield from RT.py_format(a)
        elif b.arg & 0x04 == 0x04:
            a = yield from RT.py_to_ascii(a)
            a = yield from RT.py_format(a)
        else:
            raise ValueError(f"invalid format flag {b.arg}")
        yield Prim.push(a)
    elif b.name == InstrNames.BUILD_SLICE:
        tos = yield Prim.pop()
        tos1 = yield Prim.pop()
        tos2 = yield Prim.pop()
        a = yield from RT.py_build_slice(tos2, tos1, tos)
        yield Prim.push(a)
    elif b.name == InstrNames.LOAD_METHOD:
        a = yield Prim.pop()
        a = yield from RT.py_load_method_(a, b.arg)
        yield Prim.push(a)
    elif b.name == InstrNames.CALL_METHOD:
        xs = []
        for i in range(b.arg + 2):
            a = yield Prim.pop()
            xs.append(a)
        xs.reverse()
        a = yield from RT.py_call_method(*xs)
        yield Prim.push(a)
    elif b.name == InstrNames.MAKE_FUNCTION:
        arg = b.arg
        if arg & 0x01:
            raise NotImplemented
        if arg & 0x02:
            raise NotImplemented
        if arg & 0x04:
            raise NotImplemented
        if arg & 0x08:
            name = yield Prim.pop()
            code = yield Prim.pop()
            closure = yield Prim.pop()
            a = yield from RT.py_mk_closure(name, code, closure)

        else:
            name = yield Prim.pop()
            code = yield Prim.pop()
            a = yield from RT.py_mk_func(name, code)
        yield Prim.push(a)

    elif b.name == InstrNames.CALL_FUNCTION:
        c = b.arg
        xs = []
        for i in range(c):
            a = yield Prim.pop()
            xs.append(a)
        xs.reverse()
        f = yield Prim.pop()
        a = yield from RT.py_call_func(f, *xs)
        yield Prim.push(a)

    elif b.name == InstrNames.LOAD_CLOSURE:
        arg = b.arg
        assert isinstance(arg, (bc.CellVar, bc.FreeVar))
        yield Prim.add_instr(Instr.Ref(arg.name))
    elif b.name == InstrNames.LOAD_DEREF:
        arg = b.arg
        assert isinstance(arg, (bc.CellVar, bc.FreeVar))
        yield Prim.add_instr(Instr.Deref(arg.name))
    elif b.name == InstrNames.STORE_DEREF:
        arg = b.arg
        assert isinstance(arg, (bc.CellVar, bc.FreeVar))
        yield Prim.add_instr(Instr.Setref(arg.name))


def abs_i_unary(b: bc.Instr):
    a = yield Prim.pop()
    if b.name == InstrNames.UNARY_POSITIVE:
        a = yield from RT.py_pos(a)
        yield Prim.push(a)
    elif b.name == InstrNames.UNARY_NEGATIVE:
        a = yield from RT.py_neg(a)
        yield Prim.push(a)

    elif b.name == InstrNames.UNARY_NOT:
        a = yield from RT.py_not(a)
        yield Prim.push(a)

    elif b.name == InstrNames.UNARY_INVERT:
        a = yield from RT.py_inv(a)
        yield Prim.push(a)
    else:
        raise ValueError(f"unknown unary instruction {b}")


def abs_i_jump(b: bc.Instr):
    label_name = label_to_name(b.arg)
    if b.name in (InstrNames.JUMP_FORWARD, InstrNames.JUMP_ABSOLUTE):
        yield Prim.add_instr(Instr.Jmp(label_name))

    elif b.name == InstrNames.POP_JUMP_IF_FALSE:
        a = yield Prim.pop()
        a = yield from RT.py_not(a)
        yield Prim.add_instr(Instr.JmpIf(label_name, a))
    elif b.name == InstrNames.POP_JUMP_IF_TRUE:
        a = yield Prim.pop()
        yield Prim.add_instr(Instr.JmpIf(label_name, a))
    elif b.name == InstrNames.JUMP_IF_FALSE_OR_POP:
        a = yield Prim.pop()
        o = yield from RT.py_not(a)
        yield Prim.add_instr(Instr.JmpIfPush(label_name, o, a))
    elif b.name == InstrNames.JUMP_IF_TRUE_OR_POP:
        a = yield Prim.pop()
        yield Prim.add_instr(Instr.JmpIfPush(label_name, a, a))
    else:
        raise ValueError(f"unknown jump instruction {b}")


def abs_i_binary(b: bc.Instr):
    a2 = yield Prim.pop()
    a1 = yield Prim.pop()
    if b.name == InstrNames.BINARY_POWER:
        c = yield from RT.py_pow(a1, a2)
        yield Prim.push(c)
    elif b.name == InstrNames.BINARY_MULTIPLY:
        c = yield from RT.py_mul(a1, a2)
        yield Prim.push(c)
    elif b.name == InstrNames.BINARY_MATRIX_MULTIPLY:
        c = yield from RT.py_matmul(a1, a2)
        yield Prim.push(c)
    elif b.name == InstrNames.BINARY_FLOOR_DIVIDE:
        c = yield from RT.py_floordiv(a1, a2)
        yield Prim.push(c)
    elif b.name == InstrNames.BINARY_TRUE_DIVIDE:
        c = yield from RT.py_truediv(a1, a2)
        yield Prim.push(c)
    elif b.name == InstrNames.BINARY_MODULO:
        c = yield from RT.py_mod(a1, a2)
        yield Prim.push(c)
    elif b.name == InstrNames.BINARY_ADD:
        c = yield from RT.py_add(a1, a2)
        yield Prim.push(c)
    elif b.name == InstrNames.BINARY_SUBTRACT:
        c = yield from RT.py_sub(a1, a2)
        yield Prim.push(c)
    elif b.name == InstrNames.BINARY_SUBSCR:
        c = yield from RT.py_subscr(a1, a2)
        yield Prim.push(c)
    elif b.name == InstrNames.BINARY_LSHIFT:
        c = yield from RT.py_lsh(a1, a2)
        yield Prim.push(c)
    elif b.name == InstrNames.BINARY_RSHIFT:
        c = yield from RT.py_rsh(a1, a2)
        yield Prim.push(c)
    elif b.name == InstrNames.BINARY_AND:
        c = yield from RT.py_and(a1, a2)
        yield Prim.push(c)
    elif b.name == InstrNames.BINARY_XOR:
        c = yield from RT.py_xor(a1, a2)
        yield Prim.push(c)
    elif b.name == InstrNames.BINARY_OR:
        c = yield from RT.py_or(a1, a2)
        yield Prim.push(c)
    else:
        raise ValueError(f"unknown binary instruction {b}")


def abs_i_inplace_binary(b: bc.Instr):
    a2 = yield Prim.pop()
    a1 = yield Prim.pop()
    if b.name == InstrNames.INPLACE_POWER:
        c = yield from RT.py_ipow(a1, a2)
        yield Prim.push(c)
    elif b.name == InstrNames.INPLACE_MULTIPLY:
        c = yield from RT.py_imul(a1, a2)
        yield Prim.push(c)
    elif b.name == InstrNames.INPLACE_MATRIX_MULTIPLY:
        c = yield from RT.py_imatmul(a1, a2)
        yield Prim.push(c)
    elif b.name == InstrNames.INPLACE_FLOOR_DIVIDE:
        c = yield from RT.py_ifloordiv(a1, a2)
        yield Prim.push(c)
    elif b.name == InstrNames.INPLACE_TRUE_DIVIDE:
        c = yield from RT.py_itruediv(a1, a2)
        yield Prim.push(c)
    elif b.name == InstrNames.INPLACE_MODULO:
        c = yield from RT.py_imod(a1, a2)
        yield Prim.push(c)
    elif b.name == InstrNames.INPLACE_ADD:
        c = yield from RT.py_iadd(a1, a2)
        yield Prim.push(c)
    elif b.name == InstrNames.INPLACE_SUBTRACT:
        c = yield from RT.py_isub(a1, a2)
        yield Prim.push(c)
    elif b.name == InstrNames.INPLACE_LSHIFT:
        c = yield from RT.py_ilsh(a1, a2)
        yield Prim.push(c)
    elif b.name == InstrNames.INPLACE_RSHIFT:
        c = yield from RT.py_irsh(a1, a2)
        yield Prim.push(c)
    elif b.name == InstrNames.INPLACE_AND:
        c = yield from RT.py_iand(a1, a2)
        yield Prim.push(c)
    elif b.name == InstrNames.INPLACE_XOR:
        c = yield from RT.py_ixor(a1, a2)
        yield Prim.push(c)
    elif b.name == InstrNames.INPLACE_OR:
        c = yield from RT.py_ior(a1, a2)
        yield Prim.push(c)
    else:
        raise ValueError(f"unknown binary instruction {b}")
