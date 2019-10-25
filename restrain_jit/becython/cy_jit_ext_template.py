from collections import defaultdict

from restrain_jit.jit_info import PyCodeInfo
from restrain_jit.becython.cy_jit_common import *
from string import Template
import typing

template = """
cimport restrain_jit.becython.cython_rts.RestrainJIT as RestrainJIT
from restrain_jit.becython.cython_rts.hotspot cimport pytoint, inttoptr
from libc.stdint cimport int64_t, int8_t
from libcpp.vector cimport vector as std_vector
from libcpp.cast cimport reinterpret_cast

# method type
ctypedef object (*method_t)($many_objects)

# method lookup type
ctypedef method_t (*method_get_t)($many_int64_t)

# method look up ptr
cdef method_get_t method_get

# to avoid params have conflicts against 'type'
cdef inline method_t $method_get_invoker($unnamed_args):
    func = method_get$typeids
    return func

cdef class F:
    # python compatible method to change 'method look up ptr'
    cpdef mut_method_get(self, int64_t f):
        global method_get
        method_get = reinterpret_cast[method_get_t](inttoptr(f))

    def __call__(self, $arguments):
        $method = $method_get_invoker($arguments)
        return $method($arguments)

f = F() 
"""


def mk_call_record_t(argc):
    if argc is 0:
        call_record_t = 'void*'
    elif argc is 1:
        call_record_t = '(int64_t, )'
    else:
        call_record_t = '(' + ', '.join(['int64_t'] * argc) + ')'
    return call_record_t


def mk_call_record(args):
    if not args:
        return "()"
    elif len(args) is 1:
        call_record = '(pytoint(type(%s)), )' % args[0]
    else:
        call_record = '(' + ', '.join('pytoint(type(%s))' % arg for arg in args) + ')'
    return call_record


def mk_module_code(code_info: PyCodeInfo):
    freevars = code_info.freevars
    argnames = code_info.argnames

    method_name = "method"
    method_getter_invoker_name = "invoke_method_get"

    while method_name in argnames:
        method_name += "_emm"

    while method_getter_invoker_name in argnames:
        method_name += "_emm"

    arguments = freevars + argnames
    argc = len(arguments)
    unnamed_args = ['a%d' % i for i in range(argc)]

    return Template(template).substitute(
        method=method_name,
        many_objects=', '.join(['object'] * argc),
        many_int64_t=', '.join(['int64_t'] * argc),
        unnamed_args=", ".join(unnamed_args),
        typeids=mk_call_record(unnamed_args),
        method_get_invoker=method_getter_invoker_name,
        arguments=', '.join(arguments))


build_method_getter_template = """
cimport restrain_jit.becython.cython_rts.RestrainJIT as RestrainJIT
from restrain_jit.becython.cython_rts.hotspot cimport pytoint, inttoptr
from libc.stdint cimport int64_t
from libcpp.cast cimport reinterpret_cast

ctypedef object (*method_t)($many_objects)
cdef method_t base_method = reinterpret_cast[method_t](inttoptr($base_method_addr))

$declare_all_methods

cdef method_t method_get($many_int64_args):
$hard_coded_dynamic_dispatch
    
method_get_addr = reinterpret_cast[int64_t](<void*>method_get)  
"""


def group_by(seq, f):
    res = defaultdict(list)
    for each in seq:
        res[f(each)].append(each)
    return dict(res)


def decision_recurse(m: typing.List[typing.Tuple[call_record_t, fptr_addr]],
                     argc: int,
                     depth=0):
    if depth == argc:
        assert len(m) is 1
        return m[0][1]
    groups = group_by(m, lambda x: x[0][depth])
    return {k: decision_recurse(v, argc, depth + 1) for k, v in groups.items()}


def mk_hard_coded_method_getter_module(methods: typing.Dict[call_record_t, fptr_addr],
                                       base_method_addr: fptr_addr, argc: int):

    declare_all_methods = []
    hard_coded_dynamic_dispatch = []
    many_objects = ', '.join(['object'] * argc)
    many_int64_args = ', '.join("int64_t arg%d" % i for i in range(argc))

    def codegen_jit_method_reinterp(fptr_addrs: typing.Iterable[fptr_addr]):
        for each in fptr_addrs:
            each = 'cdef method_t jit_method_{} = reinterpret_cast[method_t](inttoptr({}LL))'.format(
                each, hex(each))
            declare_all_methods.append(each)

    def codegen_dispatch_recurse(d: typing.Union[int, dict], indent="  ", argi=0):
        if isinstance(d, int):
            hard_coded_dynamic_dispatch.append("{}return jit_method_{}".format(indent, d))
            return

        for k, v in d.items():
            hard_coded_dynamic_dispatch.append("{}if {}LL == arg{}:".format(indent, hex(k), argi))
            codegen_dispatch_recurse(v, indent + "  ", argi + 1)

    m = list(methods.items())
    codegen_jit_method_reinterp(x[1] for x in m)
    dispatch = decision_recurse(m, argc)
    codegen_dispatch_recurse(dispatch)
    hard_coded_dynamic_dispatch.append('  return base_method')

    code = Template(build_method_getter_template).substitute(
        many_objects=many_objects,
        many_int64_args=many_int64_args,
        base_method_addr=base_method_addr,
        declare_all_methods='\n'.join(declare_all_methods),
        hard_coded_dynamic_dispatch='\n'.join(hard_coded_dynamic_dispatch))
    return code
