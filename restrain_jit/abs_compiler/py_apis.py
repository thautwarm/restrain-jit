import types
import bytecode as bc
from restrain_jit.vm.am import *


class NS:
    RestrainJIT = "RestrainJIT"


def py_not(a: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_not.__name__)
    a = yield app(fn, [a])
    return a


def py_pos(a: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_pos.__name__)
    a = yield app(fn, [a])
    return a


def py_is_true(a: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_is_true.__name__)
    a = yield app(fn, [a])
    return a


def py_inv(a: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_inv.__name__)
    a = yield app(fn, [a])
    return a


def py_neg(a: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_neg.__name__)
    a = yield app(fn, [a])
    return a


def py_iter(a: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_iter.__name__)
    a = yield app(fn, [a])
    return a


def py_pow(a: Repr, b: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_pow.__name__)
    a = yield app(fn, [a, b])
    return a


def py_mul(a: Repr, b: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_mul.__name__)
    a = yield app(fn, [a, b])
    return a


def py_matmul(a: Repr, b: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_matmul.__name__)
    a = yield app(fn, [a, b])
    return a


def py_floordiv(a: Repr, b: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_floordiv.__name__)
    a = yield app(fn, [a, b])
    return a


def py_truediv(a: Repr, b: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_truediv.__name__)
    a = yield app(fn, [a, b])
    return a


def py_mod(a: Repr, b: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_mod.__name__)
    a = yield app(fn, [a, b])
    return a


def py_add(a: Repr, b: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_add.__name__)
    a = yield app(fn, [a, b])
    return a


def py_sub(a: Repr, b: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_sub.__name__)
    a = yield app(fn, [a, b])
    return a


def py_subscr(a: Repr, b: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_subscr.__name__)
    a = yield app(fn, [a, b])
    return a


def py_lsh(a: Repr, b: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_lsh.__name__)
    a = yield app(fn, [a, b])
    return a


def py_rsh(a: Repr, b: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_rsh.__name__)
    a = yield app(fn, [a, b])
    return a


def py_and(a: Repr, b: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_and.__name__)
    a = yield app(fn, [a, b])
    return a


def py_xor(a: Repr, b: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_xor.__name__)
    a = yield app(fn, [a, b])
    return a


def py_or(a: Repr, b: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_or.__name__)
    a = yield app(fn, [a, b])
    return a


def py_ipow(a: Repr, b: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_ipow.__name__)
    a = yield app(fn, [a, b])
    return a


def py_imul(a: Repr, b: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_imul.__name__)
    a = yield app(fn, [a, b])
    return a


def py_imatmul(a: Repr, b: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_imatmul.__name__)
    a = yield app(fn, [a, b])
    return a


def py_ifloordiv(a: Repr, b: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_ifloordiv.__name__)
    a = yield app(fn, [a, b])
    return a


def py_itruediv(a: Repr, b: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_itruediv.__name__)
    a = yield app(fn, [a, b])
    return a


def py_imod(a: Repr, b: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_imod.__name__)
    a = yield app(fn, [a, b])
    return a


def py_iadd(a: Repr, b: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_iadd.__name__)
    a = yield app(fn, [a, b])
    return a


def py_isub(a: Repr, b: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_isub.__name__)
    a = yield app(fn, [a, b])
    return a


def py_isubscr(a: Repr, b: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_isubscr.__name__)
    a = yield app(fn, [a, b])
    return a


def py_ilsh(a: Repr, b: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_ilsh.__name__)
    a = yield app(fn, [a, b])
    return a


def py_irsh(a: Repr, b: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_irsh.__name__)
    a = yield app(fn, [a, b])
    return a


def py_iand(a: Repr, b: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_iand.__name__)
    a = yield app(fn, [a, b])
    return a


def py_ixor(a: Repr, b: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_ixor.__name__)
    a = yield app(fn, [a, b])
    return a


def py_ior(a: Repr, b: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_ior.__name__)
    a = yield app(fn, [a, b])
    return a


def py_setitem(subj, key, val):
    fn = yield from_lower(NS.RestrainJIT, py_setitem.__name__)
    yield app(fn, [subj, key, val])


def py_delitem(subj, key):
    fn = yield from_lower(NS.RestrainJIT, py_delitem.__name__)
    yield app(fn, [subj, key])


def py_printexpr(tos):
    fn = yield from_lower(NS.RestrainJIT, py_printexpr.__name__)
    yield app(fn, [tos])


def py_set_add(subj, tos):
    fn = yield from_lower(NS.RestrainJIT, py_set_add.__name__)
    yield app(fn, [subj, tos])


def py_list_append(subj, tos):
    fn = yield from_lower(NS.RestrainJIT, py_list_append.__name__)
    yield app(fn, [subj, tos])


def py_map_add(subj, tos, tos1):
    fn = yield from_lower(NS.RestrainJIT, py_map_add.__name__)
    yield app(fn, [subj, tos, tos1])


def py_to_list(tos):
    fn = yield from_lower(NS.RestrainJIT, py_to_list.__name__)
    a = yield app(fn, [tos])
    return a


def py_to_tuple(tos):
    fn = yield from_lower(NS.RestrainJIT, py_to_tuple.__name__)
    a = yield app(fn, [tos])
    return a


def py_len(tos):
    fn = yield from_lower(NS.RestrainJIT, py_len.__name__)
    a = yield app(fn, [tos])
    return a


def py_build_slice(tos2, tos1, tos):
    fn = yield from_lower(NS.RestrainJIT, py_build_slice.__name__)
    a = yield app(fn, [tos2, tos1, tos])
    return a


def py_to_str(tos):
    fn = yield from_lower(NS.RestrainJIT, py_to_str.__name__)
    a = yield app(fn, [tos])
    return a


def py_to_repr(tos):
    fn = yield from_lower(NS.RestrainJIT, py_to_repr.__name__)
    a = yield app(fn, [tos])
    return a


def py_to_ascii(tos):
    fn = yield from_lower(NS.RestrainJIT, py_to_ascii.__name__)
    a = yield app(fn, [tos])
    return a


def py_format(tos):
    fn = yield from_lower(NS.RestrainJIT, py_format.__name__)
    a = yield app(fn, [tos])
    return a


def py_load_method_(tos, attr: str):
    attr = yield const(ValSymbol(attr))
    fn = yield from_lower(NS.RestrainJIT, py_load_method_.__name__)
    a = yield app(fn, [tos, attr])
    _0 = yield const(0)
    _1 = yield const(1)
    a1 = yield from py_subscr(a, _0)
    a2 = yield from py_subscr(a, _1)
    yield push(a1)
    yield push(a2)


def py_get_attr(tos: Repr, attr: str):
    attr = yield const(ValSymbol(attr))
    fn = yield from_lower(NS.RestrainJIT, py_get_attr.__name__)
    a = yield app(fn, [tos, attr])
    return a


def py_store_attr(tos: Repr, val: Repr, attr: str):
    attr = yield const(Symbol(attr))
    fn = yield from_lower(NS.RestrainJIT, py_store_attr.__name__)
    a = yield app(fn, [tos, attr, val])
    return a


def py_del_attr(subj: Repr, attr: str):
    attr = yield const(Symbol(attr))
    fn = yield from_lower(NS.RestrainJIT, py_del_attr.__name__)
    a = yield app(fn, [subj, attr])
    return a


def py_call_method(*params: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_call_method.__name__)
    a = yield app(fn, list(params))
    return a


def py_mk_closure(closure_vars: t.List[Repr], native_fn_ptr: Repr):
    tp = yield from py_mk_tuple(closure_vars)
    mk_closure = yield from_lower(NS.RestrainJIT,
                                  py_mk_closure.__name__)
    a = yield app(mk_closure, [tp, native_fn_ptr])
    return a


class Indirect:
    """
    start a new VM object
    """
    f: 't.Callable'


def py_mk_func(name: str, code: types.CodeType):
    code = bc.Bytecode.from_code(code)
    a = yield code_info(code)
    for each in a.glob_deps:
        yield require_global(each)

    a = yield const(a)
    f = yield from_lower(NS.RestrainJIT, py_mk_func.__name__)
    n = yield const(name)
    a = yield app(f, [n, a])
    return a


def py_call_func_varargs(f, a):
    raise NotImplemented


def py_call_func_varargs_kwargs(f, a, b):
    raise NotImplemented


def py_call_func_kwargs(f, attrs: t.Tuple[str, ...], *args):
    raise NotImplemented


def py_call_func(f: Repr, *args: Repr):
    a = yield app(f, args)
    return a


def py_raise(*xs):
    """
    len(xs) = 0, 1, 2
    """
    raise NotImplemented


def py_mk_tuple(xs: t.List[Repr]):
    fn = yield from_lower(NS.RestrainJIT, py_mk_tuple.__name__)
    a = yield app(fn, xs)
    return a


def py_mk_list(xs: t.List[Repr]):
    fn = yield from_lower(NS.RestrainJIT, py_mk_list.__name__)
    a = yield app(fn, xs)
    return a


def py_mk_set(xs: t.List[Repr]):
    fn = yield from_lower(NS.RestrainJIT, py_mk_set.__name__)
    a = yield app(fn, xs)
    return a


def py_mk_map(keys: Repr, vals: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_mk_map.__name__)
    a = yield app(fn, [keys, vals])
    return a


def py_cat_strs(vs: t.List[Repr]):
    fn = yield from_lower(NS.RestrainJIT, py_cat_strs.__name__)
    a = yield app(fn, vs)
    return a


def py_is_none(v: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_is_none.__name__)
    a = yield app(fn, [v])
    return a


def yield_val(a: Repr):
    raise NotImplemented


def yield_from(a: Repr):
    raise NotImplemented


def py_eq(a: Repr, b: Repr):
    fn = from_lower(NS.RestrainJIT, py_eq.__name__)
    a = yield from app(fn, [a])
    return a


def py_neq(a: Repr, b: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_neq.__name__)
    a = yield app(fn, [a, b])
    return a


def py_is(a: Repr, b: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_is.__name__)
    a = yield app(fn, [a, b])
    return a


def py_is_not(a: Repr, b: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_is_not.__name__)
    a = yield app(fn, [a, b])
    return a


def py_lt(a: Repr, b: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_lt.__name__)
    a = yield app(fn, [a, b])
    return a


def py_le(a: Repr, b: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_le.__name__)
    a = yield app(fn, [a, b])
    return a


def py_gt(a: Repr, b: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_gt.__name__)
    a = yield app(fn, [a, b])
    return a


def py_ge(a: Repr, b: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_ge.__name__)
    a = yield app(fn, [a, b])
    return a


def py_in(a: Repr, b: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_in.__name__)
    a = yield app(fn, [a, b])
    return a


def py_not_in(a: Repr, b: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_not_in.__name__)
    a = yield app(fn, [a, b])
    return a


def py_enter(with_val: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_enter.__name__)
    with_val = yield app(fn, [with_val])
    return with_val


def py_exc_match(exc: Repr, exc_ty):
    fn = yield from_lower(NS.RestrainJIT, py_exc_match.__name__)
    with_val = yield app(fn, [exc, exc_ty])
    return with_val


def py_throw(err: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_throw.__name__)
    err = yield app(fn, [err])
    return err


def py_exit(with_val: Repr):
    fn = yield from_lower(NS.RestrainJIT, py_exit.__name__)
    yield app(fn, [with_val])


def py_none():
    a = yield const(None)
    return a


def jl_isa(a: Repr, b: Repr):
    fn = yield from_lower(NS.RestrainJIT, jl_isa.__name__)
    a = yield app(fn, [a, b])
    return a
