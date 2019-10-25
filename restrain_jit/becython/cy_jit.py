from restrain_jit.becython.cy_jit_hotspot_comp import Strategy, HitN, JITRecompilationDecision, extension_type_pxd_paths, is_jit_able_type
from restrain_jit.becython.cy_method_codegen import CodeEmit, UndefGlobal
from restrain_jit.becython.cy_jit_common import *
from restrain_jit.becython.cython_vm import CyVM
from restrain_jit.becython.cy_jit_ext_template import mk_module_code, mk_call_record_t, mk_hard_coded_method_getter_module
from restrain_jit.becython.cy_loader import compile_module, JIT_FUNCTION_DIR, JIT_TYPE_DIR, ximport_module
from restrain_jit.jit_info import PyFuncInfo, PyCodeInfo
from restrain_jit.utils import CodeOut
from restrain_jit.becython import cy_jit_common as cmc

from types import FunctionType, ModuleType

import typing as t


class JITFunctionHoldPlace:
    memoize_partial_code: t.Optional[CodeOut]
    method_arguments: t.Optional[t.Tuple[str, ...]]
    function_module: ModuleType
    base_method_module: ModuleType
    methods: t.Dict[call_record_t, fptr_addr]

    def __init__(self, jit_sys: 'JITSystem', code_info: PyCodeInfo):
        self.sys = jit_sys
        self.globals = {}
        self.methods: t.Dict[call_record_t, fptr_addr] = {}
        # do not access code_info.glob_deps,
        # due to some global var like `type`, `len` are removed from here
        self.glob_deps = ()
        self.name_that_makes_sense = code_info.name
        self.argc = code_info.argcount

        self.base_method_code = ""
        self.base_method_addr = None
        self._function_module = None
        self._fn_ptr_name = None
        self.call_recorder = None
        self.memoize_partial_code = None
        self.method_arguments = None

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

    def add_methods(self, dispatcher: t.Dict[call_record_t, t.Tuple[type, ...]]):
        if not dispatcher:
            return
        for argtypeids, argtypes in dispatcher.items():
            self.add_method(argtypeids, argtypes)

        self._rebuild_method_getter_and_set()

    def add_method(self, argtypeids: call_record_t, argtypes: t.Tuple[type, ...]):
        self.sys.add_jit_method(self, argtypeids, argtypes)

    def _rebuild_method_getter_and_set(self):
        code = mk_hard_coded_method_getter_module(self.methods, self.base_method_addr,
                                                  self.argc)
        mod = compile_module(JIT_FUNCTION_DIR, "MethodGetter", code)
        self.function_module.f.mut_method_get(mod.method_get_addr)


class JITSystem:

    def __init__(self, strategies: t.List[Strategy] = None):
        strategies = strategies or [HitN(200)]
        self.fn_count = 0
        self.jit_hotspot_analysis = JITRecompilationDecision(strategies)
        self.memoize_partial_code = {}
        self.jit_fptr_index = {}
        self.fn_place_index = {}  # type: t.Dict[int, JITFunctionHoldPlace]
        self.store_base_method_log = False

    def jitdata(self, cls: type):
        undef = object()
        anns = {}
        code = []
        imports = []
        for i, (k, t) in enumerate(cls.__annotations__.items()):
            path = extension_type_pxd_paths.get(t, undef)
            if path is undef:
                anns[k] = 'object'
            elif path is None:
                anns[k] = t.__name__
            else:
                typename = "{}{}".format(typed_head, i)
                anns[k] = typename
                imports.append('from {} cimport {} as {}'.format(
                    path, t.__name__, typename))
        code.append("cdef class {}:".format(cls.__name__))
        for attr, typestr in anns.items():
            code.append("    cdef {} x_{}".format(typestr, attr))
        code.append("    def __init__(self, {}):".format(', '.join(anns)))
        for attr, _ in anns.items():
            code.append("        self.x_{0} = {0}".format(attr))

        for attr, typestr in anns.items():
            code.append("    cpdef {1} get_{0}(self):".format(attr, typestr))
            code.append("           return self.x_{0}".format(attr))

            code.append("    @property")
            code.append("    def {0}(self):".format(attr))
            code.append("           return self.x_{0}".format(attr))

            code.append("    cpdef void set_{0}(self, {1} {0}):".format(attr, typestr))
            code.append("           self.x_{0} = {0}".format(attr))

            code.append("    @{}.setter".format(attr))
            code.append("    def {0}(self, {1} {0}):".format(attr, typestr))
            code.append("           self.x_{0} = {0}".format(attr))

        pyx = '\n'.join(imports + code)

        code.clear()
        code.append("cdef class {}:".format(cls.__name__))
        for attr, typestr in anns.items():
            code.append("    cdef {} x_{}".format(typestr, attr))
        for attr, typestr in anns.items():
            code.append("    cpdef void set_{0}(self, {1})".format(attr, typestr))
            code.append("    cpdef {1} get_{0}(self)".format(attr, typestr))

        pxd = '\n'.join(imports + code)
        mod = ximport_module(JIT_TYPE_DIR, cls.__name__, pyx, pxd)
        return getattr(mod, cls.__name__)

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
        fn_place.memoize_partial_code = code_out
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
        fn_place = JITFunctionHoldPlace(self, code_info)
        fn_place.function_module = self.generate_module_for_code(code_info)
        self.jit_fptr_index[id(fn_place)] = fn_place.function_module.f
        return fn_place

    def generate_base_method(self, function_place: JITFunctionHoldPlace, code):
        argc = function_place.argc
        method_argtype_comma_lst = ', '.join('object' for _ in range(argc))
        method_get_argument_comma_lst = ', '.join('int64_t _%d' % i for i in range(argc))
        # TODO: use auto-evolution-able method lookup
        fn_ptr_name = function_place.fn_ptr_name
        code = """
{}
ctypedef object (*method_t)({})
cdef method_t this_method_getter({}):
    return {}
base_method_addr = reinterpret_cast[int64_t](<void*>{})
method_getter_addr = reinterpret_cast[int64_t](<void*>this_method_getter)    
        """.format(code, method_argtype_comma_lst, method_get_argument_comma_lst,
                   fn_ptr_name, fn_ptr_name)

        if self.store_base_method_log:
            function_place.base_method_code = code

        unique_module = "Methods_{}_{}_base_method".format(
            id(function_place), function_place.name_that_makes_sense.replace('.', '__'))
        mod = compile_module(JIT_FUNCTION_DIR, unique_module, code)

        method_init_fptrs = getattr(mod, cmc.method_init_fptrs)
        method_init_globals = getattr(mod, cmc.method_init_globals)
        init_notifier = getattr(mod, cmc.method_init_recorder_and_notifier)
        method_getter_addr = getattr(mod, 'method_getter_addr')
        call_recorder = mod.NonJITCallRecorder()
        function_place.call_recorder = call_recorder
        init_notifier(
            call_recorder, lambda: self.jit_hotspot_analysis.trigger_jit(function_place))
        g = function_place.globals
        method_init_globals(**{k: g[k] for k in function_place.glob_deps})
        method_init_fptrs(self.jit_fptr_index)
        function_place.base_method_module = mod
        function_place.function_module.f.mut_method_get(method_getter_addr)
        function_place.base_method_addr = mod.base_method_addr

    def add_jit_method(self, function_place: JITFunctionHoldPlace,
                       argtypeids: call_record_t, argtypes: t.Tuple[type, ...]):
        method_arguments = function_place.method_arguments
        fn_ptr_name = function_place.fn_ptr_name
        actual_args = [cmc.typed_head + arg for arg in method_arguments]
        once_code_out = CodeOut()
        declaring: list = once_code_out[cmc.Import]
        typing: list = once_code_out[cmc.Customizable]

        typing.append("cdef {}({}):".format(fn_ptr_name, ', '.join(actual_args)))
        undef = object()
        for i, (actual_arg, arg, argtype) in enumerate(
                zip(actual_args, method_arguments, argtypes)):
            path = extension_type_pxd_paths.get(argtype, undef)
            if path is undef:
                # well, this type cannot JIT in fact, so still object and stop recording it.
                typing.append("{}{} = {}".format(cmc.IDENTATION_SECTION, arg, actual_arg))
            elif path is None:
                # it's builtin extension types, like dict, list, etc.
                typing.append("{}cdef {} {} = {}".format(cmc.IDENTATION_SECTION,
                                                         argtype.__name__, arg, actual_arg))
            else:
                # Good, user-defined extension types!
                # You'll see how fast it'll be!

                # Firstly we import the required type
                typename = "{}{}".format(cmc.typed_head, i)
                declaring.append('from {} cimport {} as {}'.format(
                    path, argtype.__name__, typename))
                typing.append("{}cdef {} {} = {}".format(cmc.IDENTATION_SECTION, typename,
                                                         arg, actual_arg))

        once_code_out.merge_update(function_place.memoize_partial_code)
        code = '\n'.join(once_code_out.to_code_lines())
        # TODO: use auto-evolution-able method lookup
        code = """
{}
method_addr = reinterpret_cast[int64_t](<void*>{})
        """.format(code, fn_ptr_name)

        unique_module = "Methods_{}_{}_JITed".format(
            id(function_place), function_place.name_that_makes_sense.replace('.', '__'))
        mod = compile_module(JIT_FUNCTION_DIR, unique_module, code)
        method_init_fptrs = getattr(mod, cmc.method_init_fptrs)
        method_init_globals = getattr(mod, cmc.method_init_globals)
        g = function_place.globals
        method_init_globals(**{k: g[k] for k in function_place.glob_deps})
        method_init_fptrs(self.jit_fptr_index)
        function_place.methods[argtypeids] = mod.method_addr
