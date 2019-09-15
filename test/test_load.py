import sys
import types
from importlib._bootstrap_external import _NamespacePath
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

    def __nonzero__(self):
        return bool(object.__getattribute__(self, "__py_module__"))

    def __str__(self):
        return str(object.__getattribute__(self, "__py_module__"))

    def __repr__(self):
        return repr(object.__getattribute__(self, "__py_module__"))


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
        """Try to find a spec for 'fullname' on sys.path or 'path'.

        The search is based on sys.path_hooks and sys.path_importer_cache.
        """

        def apply():
            nonlocal path
            if path is None:
                path = sys.path
            spec = cls._get_spec(fullname, path, target)
            if spec is None:
                return None
            elif spec.loader is None:
                namespace_path = spec.submodule_search_locations
                if namespace_path:
                    # We found at least one namespace path.  Return a spec which
                    # can create the namespace package.
                    spec.origin = None
                    spec.submodule_search_locations = _NamespacePath(
                        fullname, namespace_path, cls._get_spec)
                    return spec
                else:
                    return None
            else:
                return spec

        spec = apply()
        spec.loader = RePyLoader(spec.loader)
        return spec


sys.meta_path.insert(0, RePyFinder)

import a
a.b = 1
print(type(a))
print(a.__py_module__.b)
a.b = 2

print(a.__state_ages__)
