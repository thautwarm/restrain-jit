from restrain_jit.becython.cy_codegen import *
from restrain_jit.vm.am import PyFuncInfo
from types import FunctionType


class JITFunctionHoldPlace:

    def header_file(self):
        raise NotImplementedError

    def source_file(self):
        raise NotImplementedError

    def counter_name(self) -> str:
        raise NotImplementedError

    def global_name(self, glob: str) -> str:
        raise NotImplementedError

    def arg_type_name(self, ith: int) -> str:
        raise NotImplementedError


class JIT:

    def get_func_info(self, types: FunctionType) -> PyFuncInfo:
        raise NotImplementedError

    def setup(self):
        # FIXME: create the temporary directory,
        # as the place to hold all compiled extensions and,
        # the source codes required by re-JIT.
        # ONE RUNTIME USES ONE JIT DIRECTORY
        raise NotImplementedError

    def allocate_place_for_function(self, f) -> JITFunctionHoldPlace:
        # use object id and function name and module name to
        # generate unique path as well as meaningful.
        raise NotImplementedError

    def register_function(self, f: FunctionType):
        place = self.allocate_place_for_function(f)

    def codegen_no_arg_type(self):

        pass
