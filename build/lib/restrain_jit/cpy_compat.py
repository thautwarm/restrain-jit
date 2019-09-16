import sys
import types
from importlib.abc import Loader
from importlib.machinery import PathFinder
from importlib.util import module_from_spec


class RestrainModule(types.ModuleType):
    __py_module__: types.ModuleType
    __state_ages__: dict

    def __init__(self, obj):
        object.__setattr__(self, "__py_module__", obj)
        object.__setattr__(self, "__state_ages__", {})

    def __getattr__(self, name):
        return getattr(
            object.__getattribute__(self, "__py_module__"), name)

    def __delattr__(self, name):
        delattr(object.__getattribute__(self, "__py_module__"), name)

    def __setattr__(self, name, value):
        v = self.__state_ages__.get(name, 0)
        self.__state_ages__[name] = v + 1
        setattr(
            object.__getattribute__(self, "__py_module__"), name, value)


class RePyLoader(Loader):

    def __init__(self, loader: Loader):
        self.loader = loader

    def create_module(self, spec):
        spec.loader = spec.loader.loader
        mod = module_from_spec(spec)
        return RestrainModule(mod)

    def exec_module(self, module):
        self.loader.exec_module(module)

    def load_module(self, fullname):
        return RestrainModule(self.loader.load_module(fullname))


class RePyFinder(PathFinder):

    @classmethod
    def find_spec(cls, fullname, path=None, target=None):
        spec = PathFinder.find_spec(fullname, path, target)
        if spec is not None:
            spec.loader = RePyLoader(spec.loader)
        return spec


sys.meta_path.insert(0, RePyFinder)
