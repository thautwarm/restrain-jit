import sys
import types
from restrain_jit.abs_compiler import instrnames as InstrNames
from bytecode import Bytecode, Instr
from importlib import _bootstrap
from importlib._bootstrap import ModuleSpec
from importlib.abc import Loader
from contextlib import contextmanager
from importlib._bootstrap_external import PathFinder, FileLoader, ExtensionFileLoader


class RePyLoader(Loader):

    def __init__(self, loader: FileLoader):
        self.loader = loader

    def create_module(self, spec: ModuleSpec):
        # mod = RestrainModule(spec.name)
        mod = types.ModuleType(spec.name)
        _bootstrap._init_module_attrs(spec, mod)
        return mod

    def exec_module(self, module):
        """Execute the module."""
        code = self.loader.get_code(module.__name__)
        if code is None:
            raise ImportError('cannot load module {!r} when get_code() '
                              'returns None'.format(module.__name__))
        __glob_refs__ = module.__glob_refs__ = {
        }  # from a global symbol to jit functions it's referenced
        bc = Bytecode.from_code(code)

        def update_generations(name):
            functions = __glob_refs__.get(name, None)
            if functions is None:
                return
            for fn in functions:
                fn.__update_global_ref__(name)

        module.__dict__['__update_generations__'] = update_generations

        def update_bc():
            for each in bc:
                yield each
                if isinstance(
                        each,
                        Instr) and each.name == InstrNames.STORE_NAME:

                    yield Instr(
                        InstrNames.LOAD_NAME,
                        '__update_generations__',
                        lineno=each.lineno)
                    yield Instr(
                        InstrNames.LOAD_CONST,
                        each.arg,
                        lineno=each.lineno)
                    yield Instr(
                        InstrNames.CALL_FUNCTION, 1, lineno=each.lineno)
                    yield Instr(InstrNames.POP_TOP, lineno=each.lineno)

        lst = list(update_bc())
        bc.clear()
        bc.extend(lst)
        code = bc.to_code()
        exec(code, module.__dict__)


class RePyFinder(PathFinder):

    @classmethod
    def find_spec(cls, fullname, path=None, target=None):
        spec: ModuleSpec = PathFinder.find_spec(fullname, path, target)
        if spec and spec.loader and isinstance(
                spec.loader, FileLoader) and not isinstance(
                    spec.loader, ExtensionFileLoader):
            spec.loader = RePyLoader(spec.loader)
        return spec


def unregister():
    sys.meta_path.remove(RePyFinder)


def register():
    sys.meta_path.insert(0, RePyFinder)


@contextmanager
def with_registered():
    try:
        register()
        yield
    finally:
        unregister()
