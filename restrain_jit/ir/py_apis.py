import typing as t
from restrain_jit.ir import instructions as Instr, representations as Repr
from restrain_jit.ir import instrnames as InstrNames


def py_not(a: Repr.Repr):
    raise NotImplemented


def py_pos(a: Repr.Repr):
    raise NotImplemented


def py_is_true(a: Repr.Repr):
    raise NotImplemented


def py_inv(a: Repr.Repr):
    raise NotImplemented


def py_neg(a: Repr.Repr):
    raise NotImplemented


def py_iter(a: Repr.Repr):
    raise NotImplemented


def py_pow(a1, a2):
    raise NotImplemented


def py_mul(a1, a2):
    return None


def py_matmul(a1, a2):
    return None


def py_floordiv(a1, a2):
    return None


def py_truediv(a1, a2):
    return None


def py_mod(a1, a2):
    return None


def py_add(a1, a2):
    return None


def py_sub(a1, a2):
    return None


def py_subscr(a1, a2):
    return None


def py_lsh(a1, a2):
    return None


def py_rsh(a1, a2):
    return None


def py_and(a1, a2):
    return None


def py_xor(a1, a2):
    return None


def py_or(a1, a2):
    return None


def py_ipow(a1, a2):
    raise NotImplemented


def py_imul(a1, a2):
    return None


def py_imatmul(a1, a2):
    return None


def py_ifloordiv(a1, a2):
    return None


def py_itruediv(a1, a2):
    return None


def py_imod(a1, a2):
    return None


def py_iadd(a1, a2):
    return None


def py_isub(a1, a2):
    return None


def py_isubscr(a1, a2):
    return None


def py_ilsh(a1, a2):
    return None


def py_irsh(a1, a2):
    return None


def py_iand(a1, a2):
    return None


def py_ixor(a1, a2):
    return None


def py_ior(a1, a2):
    return None


def py_setitem(tos1, tos, tos2):
    return None


def py_delitem(tos1, tos):
    return None


def py_printexpr(tos):
    return None


def py_set_add(subj, tos):
    return None


def py_list_append(subj, tos):
    return None


def py_map_add(subj, tos, tos1):
    return None


def py_to_list(tos):
    return None


def py_to_tuple(tos):
    return None


def py_len(tos):
    return None


def py_build_slice(tos2, tos1, tos):
    return None


def py_to_str(tos):
    return None


def py_to_repr(tos):
    return None


def py_to_ascii(tos):
    return None


def py_format(tos):
    return None


def py_load_method_(tos, attr: str):
    return None


def py_get_attr(tos, attr: str):
    return None


def py_store_attr(tos, val, attr: str):
    return None


def py_call_method(*params):
    return None


def py_mk_closure(*params):
    return None


def py_mk_func(*params):
    return None


def py_call_func_varargs(f, a):
    return None


def py_call_func_varargs_kwargs(f, a, b):
    return None


def py_call_func_kwargs(f, attrs: t.Tuple[str, ...], *args):
    return None


def py_call_func(f, *args):
    return None


def py_raise(*xs):
    """
    len(xs) = 0, 1, 2
    """
    return None


def py_del_attr(subj, arg):
    return None


def py_mk_tuple(xs):
    return None


def py_mk_list(xs):
    return None


def py_mk_set(xs):
    return None


def py_mk_map(param):
    return None


def py_mk_const_key_map(ks, vs):
    return None


def py_cat_strs(vs):
    return None