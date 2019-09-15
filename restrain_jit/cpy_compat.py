import sys
import types
from importlib.abc import MetaPathFinder, Loader
from importlib.machinery import ModuleSpec
from importlib.util import find_spec


class MyModule(types.ModuleType):

    def __init__(self, m: ModuleSpec):

        self.m = m

    def __getattr__(self, item):
        print(item)
        return getattr(self.m, item)

    def __setattr__(self, key, value):
        print('set', key)
        setattr(self.m, key, value)


class RePyLoad(Loader):

    def create_module(self, spec):
        pass


sys.meta_path.insert(0, RePyLoad())
