from string import Template

from restrain_jit.jit_info import PyCodeInfo

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
    func = method_get($typeids)
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
        typeids=", ".join(
            "pytoint(type(%s))" % unnamed_arg for unnamed_arg in unnamed_args),
        method_get_invoker=method_getter_invoker_name,
        arguments=', '.join(arguments))
