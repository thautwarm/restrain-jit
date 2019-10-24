from restrain_jit.becython.cy_method_codegen import CodeEmit
from restrain_jit.becython.cython_vm import CyVM
from restrain_jit.becython.cy_jit_ext_template import mk_module_code
from restrain_jit.becython.cy_loader import compile_module
from restrain_jit.jit_info import PyFuncInfo, PyCodeInfo
from restrain_jit.utils import CodeOut
from types import FunctionType


class JITFunctionHoldPlace:

    def __init__(self, code_info: PyCodeInfo):
        self.globals = {}
        self.glob_deps = code_info.glob_deps
        self.name_that_makes_sense = code_info.name
        self.argc = code_info.argcount
        self._function_module = None
        self._fn_ptr_name = None

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

    def __init__(self):
        self.memoize_partial_code = {}
        self.jit_fptr_index = {}

    def jit(self, f: FunctionType):
        func_info = self.get_func_info(f)
        code_info = func_info.r_codeinfo
        fn_place = self.allocate_place_for_function(code_info)
        fn_place.globals_from(func_info.r_globals)
        CodeEmit(self, code_info, fn_place)
        return fn_place.function_module.f

    @staticmethod
    def get_func_info(f: FunctionType) -> PyFuncInfo:
        return CyVM.func_info(f)

    @staticmethod
    def generate_module_for_code(code_info: PyCodeInfo):
        code = mk_module_code(code_info)
        mod = compile_module('Functions__' + code_info.__module__.replace('.', '__'), code)
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
        method_argtype_comma_lst = ', '.join('object' for _ in range(function_place.argc))
        method_get_argument_comma_lst = ', '.join(
            'int64_t _%d' % i for i in range(function_place.argc))

        # TODO: use auto-evolution-able method lookup
        method_getter_code = """
ctypedef object (*method_t)({})
cdef method_t base_method_getter({}):
    return {}

base_method_getter_addr = reinterpret_cast[int64_t](<void*>base_method_getter)    
        """.format(method_argtype_comma_lst, method_get_argument_comma_lst,
                   function_place.fn_ptr_name)

        code += method_getter_code
        mod = compile_module(
            "Methods__" + function_place.name_that_makes_sense.replace('.', '__') +
            '__base_method', code)

        method_init_fptrs = getattr(mod, CodeEmit.method_init_fptrs)
        method_init_globals = getattr(mod, CodeEmit.method_init_globals)
        base_method_getter_addr = getattr(mod, 'base_method_getter_addr')

        g = function_place.globals
        method_init_globals(**{k: g[k] for k in function_place.glob_deps})
        method_init_fptrs(self.jit_fptr_index)

        function_place.function_module.f.mut_method_get(base_method_getter_addr)
