from restrain_jit.becython.cy_jit_hotspot_comp import Strategy, HitN, JITRecompilationDecision, extension_type_pxd_paths, is_jit_able_type
from restrain_jit.becython.cy_method_codegen import CodeEmit, UndefGlobal
from restrain_jit.becython.cython_vm import CyVM
from restrain_jit.becython.cy_jit_ext_template import mk_module_code, mk_call_record_t
from restrain_jit.becython.cy_loader import compile_module, JIT_FUNCTION_DIR, JIT_TYPE_DIR
from restrain_jit.jit_info import PyFuncInfo, PyCodeInfo
from restrain_jit.utils import CodeOut
from types import FunctionType
import typing as t


class JITFunctionHoldPlace:

    def __init__(self, code_info: PyCodeInfo):
        self.globals = {}
        # do not access code_info.glob_deps,
        # due to some global var like `type`, `len` are removed from here
        self.glob_deps = ()
        self.name_that_makes_sense = code_info.name
        self.argc = code_info.argcount

        self.base_method_code = ""
        self._function_module = None
        self._fn_ptr_name = None
        self.call_records = None

    @property
    def function_module(self):
        assert self._function_module
        return self._function_module

    @function_module.setter
    def function_module(self, v):
        self._function_module = v

    @property
    def fn_ptr_name(self):
        assert self._fn_ptr_name
        return self._fn_ptr_name

    @fn_ptr_name.setter
    def fn_ptr_name(self, v):
        self._fn_ptr_name = v

    @property
    def unique_index(self):
        return id(self)

    def counter_name(self) -> str:
        raise NotImplementedError

    def globals_from(self, globs: dict):
        self.globals = globs


class JITSystem:

    def __init__(self, strategies: t.List[Strategy] = None):
        strategies = strategies or [HitN(200)]
        self.fn_count = 0
        self.jit_hotspot_analysis = JITRecompilationDecision(strategies)
        self.memoize_partial_code = {}
        self.jit_fptr_index = {}
        self.fn_place_index = {}  # type: t.Dict[int, JITFunctionHoldPlace]
        self.store_base_method_log = False

    def jit(self, f: FunctionType):
        func_info = self.get_func_info(f)
        code_info = func_info.r_codeinfo
        fn_place = self.allocate_place_for_function(code_info)
        fn_place.globals_from(func_info.r_globals)
        CodeEmit(self, code_info, fn_place)
        f = fn_place.function_module.f
        self.fn_place_index[id(f)] = fn_place
        return f

    @staticmethod
    def get_func_info(f: FunctionType) -> PyFuncInfo:
        return CyVM.func_info(f)

    def generate_module_for_code(self, code_info: PyCodeInfo):
        code = mk_module_code(code_info)
        unique_module_name = "Functions_{}".format(self.fn_count)
        mod = compile_module(JIT_FUNCTION_DIR, unique_module_name, code)
        return mod

    def remember_partial_code(self, fn_place: JITFunctionHoldPlace, code_out: CodeOut):
        self.memoize_partial_code[id(fn_place)] = code_out

    def setup(self):
        # FIXME: create the temporary directory,
        # as the place to hold all compiled extensions and,
        # the source codes required by re-JIT.
        # ONE RUNTIME USES ONE JIT DIRECTORY
        raise NotImplementedError

    def allocate_place_for_function(self, code_info: PyCodeInfo) -> JITFunctionHoldPlace:
        # use object id and function name and module name to
        # generate unique path as well as meaningful.
        fn_place = JITFunctionHoldPlace(code_info)
        fn_place.function_module = self.generate_module_for_code(code_info)
        self.jit_fptr_index[id(fn_place)] = fn_place.function_module.f
        return fn_place

    def generate_base_method(self, function_place: JITFunctionHoldPlace, code):
        argc = function_place.argc
        method_argtype_comma_lst = ', '.join('object' for _ in range(argc))
        method_get_argument_comma_lst = ', '.join('int64_t _%d' % i for i in range(argc))

        monitor_code = ""
        if argc:
            monitor_code = """
    cdef call_record_t call_record = ({})
    call_records.record(call_record)
    if call_records.check_bounded():
        notify_jit_recompilation()
""".format(''.join('typeid(_%d), ' % i for i in range(argc)))
        call_record_t = mk_call_record_t(argc)
        # TODO: use auto-evolution-able method lookup
        code = """
{}
ctypedef ({}) call_record_t
ctypedef std_vector[call_record_t] call_records_t

cdef class NonJITCallRecords:
    cdef call_records_t records
    cdef int64_t bound
    
    def __init__(self):
        self.bound = {}
        self.records = call_records_t()
    
    cdef record(self, call_record_t m):
        self.records.push_back(m)
    
    cdef int8_t check_bounded(self):
        return self.records.size() % self.bound == 0
    
    def load_type(self, int64_t i):
        return <object>(inttoptr(i))
     
    def get(self):
        return self.records

ctypedef object (*method_t)({})
cdef NonJITCallRecords call_records 
cdef object notify_jit_recompilation
cdef method_t base_method_getter({}):
    {}
    return {}

def init_notifier(o, m):
    global notify_jit_recompilation, call_records
    call_records = m
    notify_jit_recompilation = o

base_method_getter_addr = reinterpret_cast[int64_t](<void*>base_method_getter)    
        """.format(code, call_record_t, 200, method_argtype_comma_lst,
                   method_get_argument_comma_lst, monitor_code, function_place.fn_ptr_name)

        if self.store_base_method_log:
            function_place.base_method_code = code

        unique_module = "Methods_{}_{}_base_method".format(
            id(function_place), function_place.name_that_makes_sense.replace('.', '__'))
        mod = compile_module(JIT_FUNCTION_DIR, unique_module, code)

        method_init_fptrs = getattr(mod, CodeEmit.method_init_fptrs)
        method_init_globals = getattr(mod, CodeEmit.method_init_globals)
        base_method_getter_addr = getattr(mod, 'base_method_getter_addr')
        init_notifier = getattr(mod, 'init_notifier')
        call_records = mod.NonJITCallRecords()
        function_place.call_records = call_records

        init_notifier(lambda: print("notified but do nothing..."), call_records)
        g = function_place.globals
        method_init_globals(**{k: g[k] for k in function_place.glob_deps})
        method_init_fptrs(self.jit_fptr_index)

        function_place.function_module.f.mut_method_get(base_method_getter_addr)
