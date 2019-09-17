import types
import bytecode as bc
import typing as t
from restrain_jit.abs_compiler import instrnames as InstrNames
from restrain_jit.abs_compiler import py_apis as RT
from restrain_jit.vm import am


def label_to_name(label: t.Union[bc.BasicBlock]):
    return f"block-{id(label):x}"


def pop_n(n: int):
    xs = []
    for i in range(n):
        a = yield am.pop()
        xs.append(a)
    xs.reverse()
    return xs


def abs_i(b: t.Union[bc.Instr]):
    if b.name == InstrNames.COMPARE_OP:
        yield from abs_i_cmp(b)
    elif "JUMP" in b.name:
        yield from abs_i_jump(b)
    elif b.name.startswith('UNARY'):
        yield from abs_i_unary(b)
    elif b.name.startswith('BINARY'):
        yield from abs_i_binary(b)
    elif b.name.startswith('INPLACE'):
        yield from abs_i_inplace_binary(b)
    elif b.name == InstrNames.ROT_TWO:
        a1 = yield am.pop()
        a2 = yield am.pop()
        yield am.push(a2)
        yield am.push(a1)
    elif b.name == InstrNames.ROT_THREE:
        a1 = yield am.pop()
        a2 = yield am.pop()
        a3 = yield am.pop()
        yield am.push(a3)
        yield am.push(a1)
        yield am.push(a2)
    elif b.name == InstrNames.NOP:
        pass
    elif b.name == InstrNames.DUP_TOP:
        a = yield am.pop()
        yield am.push(a)
        yield am.push(a)
    elif b.name == InstrNames.DUP_TOP_TWO:
        a = yield am.peek(0)
        yield am.push(a)
        yield am.push(a)

    elif b.name == InstrNames.GET_ITER:
        a = yield am.pop()
        a = yield from RT.py_iter(a)
        yield am.push(a)

    elif b.name == InstrNames.GET_YIELD_FROM_ITER:
        a = yield am.pop()
        a = yield from RT.py_iter(a)
        yield am.push(a)
    elif b.name == InstrNames.STORE_SUBSCR:
        tos = yield am.pop()
        tos1 = yield am.pop()
        tos2 = yield am.pop()
        yield from RT.py_setitem(tos1, tos, tos2)
    elif b.name == InstrNames.DELETE_SUBSCR:
        tos = yield am.pop()
        tos1 = yield am.pop()
        yield from RT.py_delitem(tos1, tos)
    elif b.name == InstrNames.PRINT_EXPR:
        tos = yield am.pop()
        yield from RT.py_printexpr(tos)
    elif b.name == InstrNames.SET_ADD:
        tos = yield am.pop()
        subj = yield am.peek(b.arg - 1)  # TODO: check correctness
        yield from RT.py_set_add(subj, tos)
    elif b.name == InstrNames.LIST_APPEND:
        tos = yield am.pop()
        subj = yield am.peek(b.arg - 1)
        yield from RT.py_list_append(subj, tos)
    elif b.name == InstrNames.MAP_ADD:
        tos = yield am.pop()
        tos1 = yield am.pop()
        subj = yield am.peek(b.arg - 1)
        yield from RT.py_map_add(subj, tos, tos1)
    elif b.name == InstrNames.RETURN_VALUE:
        a = yield am.pop()
        yield am.ret(a)
    elif b.name == InstrNames.YIELD_VALUE:
        a = yield am.pop()
        yield from RT.yield_val(a)

    elif b.name == InstrNames.YIELD_FROM:
        a = yield am.pop()
        yield from RT.yield_from(a)
    elif b.name == InstrNames.STORE_NAME:
        assert isinstance(b.arg, str)
        raise NotImplemented
    elif b.name == InstrNames.DELETE_NAME:
        raise NotImplemented
    elif b.name == InstrNames.UNPACK_SEQUENCE:
        val = yield am.pop()
        val = yield from RT.py_to_tuple(val)
        for idx in range(b.arg):
            idx = yield am.const(idx)
            a = yield from RT.py_subscr(val, idx)
            yield am.push(a)
    elif b.name == InstrNames.UNPACK_EX:
        val = yield am.pop()
        val = yield from RT.py_to_tuple(val)
        n = yield from RT.py_len(val)
        tail = b.arg // 256
        init = b.arg % 256
        start_idx = None
        for start_idx in range(init):
            start_idx = am.const(start_idx)
            a = yield from RT.py_subscr(val, start_idx)
            yield am.push(a)

        start_idx = yield am.const(start_idx)

        tail = yield am.const(tail)
        _1 = yield am.const(1)
        end_idx = yield from RT.py_sub(n, tail)
        a = yield from RT.py_build_slice(start_idx, _1, end_idx)
        yield am.push(a)

        for end_idx in range(init):
            off = yield am.const(end_idx + 1)
            end_idx = yield from RT.py_sub(n, off)
            a = yield from RT.py_subscr(val, end_idx)
            yield am.push(a)

    elif b.name == InstrNames.FORMAT_VALUE:
        a = yield am.pop()
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
        yield am.push(a)
    elif b.name == InstrNames.BUILD_SLICE:
        tos = yield am.pop()
        tos1 = yield am.pop()
        tos2 = yield am.pop()
        a = yield from RT.py_build_slice(tos2, tos1, tos)
        yield am.push(a)
    elif b.name == InstrNames.LOAD_METHOD:
        a = yield am.pop()
        yield from RT.py_load_method_(a, b.arg)
    elif b.name == InstrNames.CALL_METHOD:
        xs = yield from pop_n(b.arg + 2)
        a = yield from RT.py_call_method(*xs)
        yield am.push(a)
    elif b.name == InstrNames.MAKE_FUNCTION:
        arg = b.arg
        if arg & 0x01:
            raise NotImplemented
        if arg & 0x02:
            raise NotImplemented
        if arg & 0x04:
            raise NotImplemented
        if arg & 0x08:
            name = yield am.pop()
            code = yield am.pop()
            code = yield am.from_const(code)
            assert isinstance(code, types.CodeType)
            closure = yield am.pop()
            fpr = yield from RT.py_mk_func(name, code)
            a = yield from RT.py_mk_closure(closure, fpr)

        else:
            name = yield am.pop()
            code = yield am.pop()
            code = yield am.from_const(code)
            assert isinstance(code, types.CodeType)
            a = yield from RT.py_mk_func(name, code)
        yield am.push(a)

    elif b.name == InstrNames.CALL_FUNCTION:
        c = b.arg
        xs = yield from pop_n(c)
        f = yield am.pop()
        a = yield from RT.py_call_func(f, *xs)
        yield am.push(a)

    elif b.name == InstrNames.LOAD_CLOSURE:
        arg = b.arg
        assert isinstance(arg, (bc.CellVar, bc.FreeVar))
        a = yield am.reg_of(arg.name)
        yield am.push(a)

    elif b.name == InstrNames.LOAD_DEREF:
        arg = b.arg
        assert isinstance(arg, (bc.CellVar, bc.FreeVar))
        reg = yield am.reg_of(arg.name)
        a = yield am.load(reg)
        yield am.push(a)

    elif b.name == InstrNames.STORE_DEREF:
        arg = b.arg
        assert isinstance(arg, (bc.CellVar, bc.FreeVar))

        a = yield am.pop()
        yield am.store(arg.name, a)

    elif b.name == InstrNames.LOAD_FAST:
        assert isinstance(b.arg, str)
        reg = yield am.reg_of(b.arg)
        yield am.push(reg)

    elif b.name == InstrNames.STORE_FAST:
        assert isinstance(b.arg, str)
        v = yield am.pop()
        yield am.assign(b.arg, v)

    elif b.name == InstrNames.LOAD_GLOBAL:
        arg = b.arg
        assert isinstance(arg, str)
        a = yield am.from_higher("", arg)
        yield am.push(a)

    elif b.name == InstrNames.STORE_GLOBAL:
        raise NotImplemented

    elif b.name == InstrNames.LOAD_CONST:
        arg = b.arg
        a = yield am.const(arg)
        yield am.push(a)

    elif b.name == InstrNames.STORE_ATTR:
        tos = yield am.pop()
        val = yield am.pop()
        yield from RT.py_store_attr(tos, val, b.arg)

    elif b.name == InstrNames.LOAD_ATTR:
        tos = yield am.pop()
        a = yield from RT.py_get_attr(tos, b.arg)
        yield am.push(a)

    elif b.name == InstrNames.DELETE_ATTR:
        tos = yield am.pop()
        yield from RT.py_del_attr(tos, b.arg)

    elif b.name == InstrNames.BUILD_TUPLE:
        xs = yield from pop_n(b.arg)
        a = yield from RT.py_mk_tuple(xs)
        yield am.push(a)

    elif b.name == InstrNames.BUILD_LIST:
        xs = yield from pop_n(b.arg)
        a = yield from RT.py_mk_list(xs)
        yield am.push(a)

    elif b.name == InstrNames.BUILD_SET:
        xs = yield from pop_n(b.arg)
        a = yield from RT.py_mk_set(xs)
        yield am.push(a)

    elif b.name == InstrNames.BUILD_MAP:
        xs = yield from pop_n(2 * b.arg)
        ks = xs[::2]
        vs = xs[1::2]
        ks = yield from RT.py_mk_tuple(ks)
        vs = yield from RT.py_mk_tuple(vs)
        a = yield from RT.py_mk_map(ks, vs)
        yield am.push(a)

    elif b.name == InstrNames.BUILD_CONST_KEY_MAP:
        ks = yield am.pop()
        vs = yield from pop_n(b.arg)
        vs = yield from RT.py_mk_tuple(vs)
        a = yield from RT.py_mk_map(ks, vs)
        yield a.push(a)

    elif b.name == InstrNames.BUILD_STRING:
        xs = yield from pop_n(b.arg)
        a = yield from RT.py_cat_strs(xs)
        yield am.push(a)

    elif b.name == InstrNames.FOR_ITER:
        f = yield am.pop()
        a = yield from RT.py_call_func(f)
        label = b.arg
        assert isinstance(label, bc.BasicBlock)
        check_if_nothing = yield from RT.py_is_none(a)
        yield am.jump_if(label_to_name(label), check_if_nothing)
        _0 = yield am.const(0)
        _1 = yield am.const(1)
        elt = yield from RT.py_subscr(a, _0)
        st = yield from RT.py_subscr(a, _1)
        yield am.push(st)
        yield am.push(elt)

    elif b.name == InstrNames.GET_ITER:
        a = yield am.pop()
        a = yield from RT.py_get_attr(a, "__next__")
        yield am.push(a)

    elif b.name == InstrNames.SETUP_LOOP:
        pass
    elif b.name == InstrNames.POP_BLOCK:
        pass
    elif b.name == InstrNames.POP_TOP:
        yield am.pop()
    elif b.name == InstrNames.SETUP_WITH:
        arg = b.arg
        assert isinstance(arg, bc.BasicBlock)
        end_label = label_to_name(arg)
        meta = yield am.meta()
        var = yield am.pop()

        def unwind():
            # python 'with' block exits with a pushed 'None'
            yield am.pop()
            yield am.pop_block()
            yield from RT.py_exit(var)

        meta[end_label] = unwind
        entered = yield from RT.py_enter(var)
        yield am.push(entered)
        yield am.push_block(end_label)
    elif b.name == InstrNames.END_FINALLY:
        exc = yield am.pop_exception()
        label_no_ext = yield am.alloc()
        py_none = yield from RT.py_none()
        exc_is_none = yield from RT.py_is(py_none, exc)
        yield am.jump_if(label_no_ext, exc_is_none)
        yield from RT.py_throw(exc)
        yield am.label(label_no_ext)

    elif b.name == InstrNames.SETUP_FINALLY:
        arg = b.arg
        assert isinstance(arg, bc.BasicBlock)
        end_label = label_to_name(arg)
        meta = yield am.meta()

        def unwind():
            yield am.pop_block()

        meta[end_label] = unwind
        yield am.push_block(end_label)
    elif b.name == InstrNames.SETUP_EXCEPT:
        arg = b.arg
        assert isinstance(arg, bc.BasicBlock)
        end_label = label_to_name(arg)
        meta = yield am.meta()

        def unwind():
            yield am.pop_block()
            exc = yield am.pop_exception(must=True)
            py_none = yield from RT.py_none()
            yield am.push(py_none)
            yield am.push(exc)
            yield am.push(py_none)

        meta[end_label] = unwind
        yield am.push_block(end_label)
    elif b.name in (InstrNames.WITH_CLEANUP_FINISH,
                    InstrNames.WITH_CLEANUP_START,
                    InstrNames.POP_EXCEPT):
        pass
    elif b.name == InstrNames.RAISE_VARARGS:
        c = b.arg
        if c is not 1:
            raise ValueError(
                "Raise statement must take 1 argument due to the limitations of current implementation."
            )
        err = yield am.pop()
        yield from RT.py_throw(err)
    else:
        raise NotImplementedError(f"instruction {b} not supported yet")


u_map = {
    InstrNames.UNARY_POSITIVE: RT.py_pos,
    InstrNames.UNARY_NEGATIVE: RT.py_neg,
    InstrNames.UNARY_NOT: RT.py_not,
    InstrNames.UNARY_INVERT: RT.py_inv
}


def abs_i_unary(b: bc.Instr):
    a = yield am.pop()
    f = u_map.get(b.name, None)
    if f is None:
        raise ValueError(f"unknown unary instruction {b}")
    a = yield from f(a)
    yield am.push(a)


def abs_i_jump(b: bc.Instr):
    label_name = label_to_name(b.arg)
    if b.name in (InstrNames.JUMP_FORWARD, InstrNames.JUMP_ABSOLUTE):
        yield am.jump(label_name)

    elif b.name == InstrNames.POP_JUMP_IF_FALSE:
        a = yield am.pop()
        a = yield from RT.py_not(a)
        yield am.jump_if(label_name, a)
    elif b.name == InstrNames.POP_JUMP_IF_TRUE:
        a = yield am.pop()
        yield am.jump_if(label_name, a)
    elif b.name == InstrNames.JUMP_IF_FALSE_OR_POP:
        a = yield am.pop()
        o = yield from RT.py_not(a)
        yield am.jump_if_push(label_name, o, a)
    elif b.name == InstrNames.JUMP_IF_TRUE_OR_POP:
        a = yield am.pop()
        yield am.jump_if_push(label_name, a, a)
    else:
        raise ValueError(f"unknown jump instruction {b}")


bin_map = {
    InstrNames.BINARY_POWER: RT.py_pow,
    InstrNames.BINARY_MULTIPLY: RT.py_mul,
    InstrNames.BINARY_MATRIX_MULTIPLY: RT.py_matmul,
    InstrNames.BINARY_FLOOR_DIVIDE: RT.py_floordiv,
    InstrNames.BINARY_TRUE_DIVIDE: RT.py_truediv,
    InstrNames.BINARY_MODULO: RT.py_mod,
    InstrNames.BINARY_ADD: RT.py_add,
    InstrNames.BINARY_SUBTRACT: RT.py_sub,
    InstrNames.BINARY_SUBSCR: RT.py_subscr,
    InstrNames.BINARY_LSHIFT: RT.py_lsh,
    InstrNames.BINARY_RSHIFT: RT.py_rsh,
    InstrNames.BINARY_AND: RT.py_and,
    InstrNames.BINARY_XOR: RT.py_xor,
    InstrNames.BINARY_OR: RT.py_or,
}


def abs_i_binary(b: bc.Instr):
    a2 = yield am.pop()
    a1 = yield am.pop()
    f = bin_map.get(b.name, None)
    if f is None:
        raise ValueError(f"unknown binary instruction {b}")
    c = yield from f(a1, a2)
    yield am.push(c)


ibin_map = {
    InstrNames.INPLACE_POWER: RT.py_ipow,
    InstrNames.INPLACE_MULTIPLY: RT.py_imul,
    InstrNames.INPLACE_MATRIX_MULTIPLY: RT.py_imatmul,
    InstrNames.INPLACE_FLOOR_DIVIDE: RT.py_ifloordiv,
    InstrNames.INPLACE_TRUE_DIVIDE: RT.py_itruediv,
    InstrNames.INPLACE_MODULO: RT.py_imod,
    InstrNames.INPLACE_ADD: RT.py_iadd,
    InstrNames.INPLACE_SUBTRACT: RT.py_isub,
    InstrNames.INPLACE_LSHIFT: RT.py_ilsh,
    InstrNames.INPLACE_RSHIFT: RT.py_irsh,
    InstrNames.INPLACE_AND: RT.py_iand,
    InstrNames.INPLACE_XOR: RT.py_ixor,
    InstrNames.INPLACE_OR: RT.py_ior,
}


def abs_i_inplace_binary(b: bc.Instr):
    a2 = yield am.pop()
    a1 = yield am.pop()
    f = ibin_map.get(b.name, None)
    if f is None:
        raise ValueError(f"unknown binary instruction {b}")
    c = yield from f(a1, a2)
    yield am.push(c)


cmp_map = {
    bc.Compare.EQ: RT.py_eq,
    bc.Compare.NE: RT.py_neq,
    bc.Compare.IS: RT.py_is,
    bc.Compare.IS_NOT: RT.py_is_not,
    bc.Compare.LT: RT.py_lt,
    bc.Compare.LE: RT.py_le,
    bc.Compare.GT: RT.py_gt,
    bc.Compare.GE: RT.py_ge,
    bc.Compare.IN: RT.py_in,
    bc.Compare.NOT_IN: RT.py_not_in,
    bc.Compare.EXC_MATCH: RT.py_exc_match
}


def abs_i_cmp(b: bc.Instr):
    arg: bc.Compare = b.arg
    f = cmp_map[arg]
    a2 = yield am.pop()
    a1 = yield am.pop()
    a = yield from f(a1, a2)
    yield am.push(a)


def abs_i_cfg(b: bc.ControlFlowGraph):
    for each in b:
        assert isinstance(each, bc.BasicBlock)
        label_name = label_to_name(each)
        last_label = yield am.last_block_end()
        if last_label == label_name:
            meta = yield am.meta()
            unwind = meta[label_name]
            yield from unwind()
        yield am.label(label_name)
        for instr in each:
            yield from abs_i(instr)


"""

    elif b.name == InstrNames.RAISE_VARARGS:
        c = b.arg
        xs = []
        for _ in range(c):
            a = yield Prim.pop()
            xs.append(a)
        xs.reverse()
        yield from RT.py_raise(*xs)
        
    elif b.name == InstrNames.CALL_FUNCTION_EX:
        a = yield am.pop()
        arg = b.arg
        if arg is 0:
            f = yield Prim.pop()
            r = yield from RT.py_call_func_varargs(f, a)
        elif arg is 1:
            kw = a
            tp = yield Prim.pop()
            f = yield Prim.pop()
            r = yield from RT.py_call_func_varargs_kwargs(f, tp, kw)
        else:
            raise ValueError(f"invalid CALL_FUNCTION_EX flag {arg}")
        yield Prim.push(r)
    elif b.name == InstrNames.CALL_FUNCTION_KW:
        c = b.arg
        attrs = yield Prim.pop()
        assert isinstance(attrs, Repr.Const)
        attrs = attrs.val
        assert isinstance(attrs, tuple)
        xs = []
        for i in range(c):
            a = yield Prim.pop()
            xs.append(a)
        xs.reverse()
        f = yield Prim.pop()
        a = yield from RT.py_call_func_kwargs(f, attrs, *xs)
        yield Prim.push(a)
"""
