import sys
import builtins
import types
from restrain_jit.abs_compiler import instrnames as InstrNames
from bytecode import Bytecode, Instr
from importlib import _bootstrap
from importlib._bootstrap import ModuleSpec
from importlib.abc import Loader
from importlib._bootstrap_external import PathFinder, FileLoader, ExtensionFileLoader


def _inc_generation(generations, name):
    v = generations.get(name, 0)
    generations[name] = v + 1


class RestrainModule:
    __obj_generations__: dict

    def _inc_generation(self, name):
        _inc_generation(self.__obj_generations__, name)

    def __init__(self, name):
        object.__setattr__(self, "__obj_generations__", {})

    def __delattr__(self, name):
        self._inc_generation(name)
        return object.__delattr__(self, name)

    def __setattr__(self, name, value):
        self._inc_generation(name)
        return object.__setattr__(self, name, value)


class WorldCounterProxy(dict):

    def __init__(self, base, generations):
        self.update(base)
        self.generations = generations

    def _inc_generation(self, name):
        _inc_generation(self.generations, name)

    def __setitem__(self, name, value):
        self._inc_generation(name)
        dict.__setitem__(self, name, value)

    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            return builtins.__dict__[item]

    def __delitem__(self, item):
        self._inc_generation(item)
        dict.__delitem__(self, item)


class RePyLoader(Loader):

    def __init__(self, loader: FileLoader):
        self.loader = loader

    def create_module(self, spec: ModuleSpec):
        # mod = RestrainModule(spec.name)
        mod = types.ModuleType(spec.name)
        _bootstrap._init_module_attrs(spec, mod)
        return mod

    def exec_module(self, module: RestrainModule):
        """Execute the module."""
        code = self.loader.get_code(module.__name__)
        if code is None:
            raise ImportError('cannot load module {!r} when get_code() '
                              'returns None'.format(module.__name__))
        __obj_generations__ = module.__obj_generations__ = {}
        bc = Bytecode.from_code(code)

        def update_generations(name):
            age = __obj_generations__.get(name, 0)
            __obj_generations__[name] = age + 1

        def update_bc():
            for each in bc:
                yield each
                if isinstance(
                        each,
                        Instr) and each.name == InstrNames.STORE_NAME:
                    yield Instr(
                        InstrNames.LOAD_CONST,
                        update_generations,
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

    def load_module(self, fullname):
        return RestrainModule(self.loader.load_module(fullname))


class RePyFinder(PathFinder):

    @classmethod
    def find_spec(cls, fullname, path=None, target=None):
        spec: ModuleSpec = PathFinder.find_spec(fullname, path, target)
        if spec and spec.loader and isinstance(
                spec.loader, FileLoader) and not isinstance(
                    spec.loader, ExtensionFileLoader):
            spec.loader = RePyLoader(spec.loader)
        return spec


sys.meta_path.insert(0, RePyFinder)
