import tempfile
import os
import platform
import sys
from importlib import util
from restrain_jit.config import RESTRAIN_CONFIG
from pathlib import Path
from string import Template
from restrain_jit.utils import exec_cc
try:
    import Cython.Includes as includes
except ImportError:
    raise RuntimeError(
        "For using Cython backend, cython package is required.")
include_paths = list(includes.__path__)

suffix = '.pyd' if platform.system() == 'Windows' else '.so'

template = Template(r"""
from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

exts = [
    Extension($module,
        [$module_path],
        include_dirs=$include_dirs,
        libraries=$libraries,
        library_dirs=$library_dirs,
        language="c++"
    )
]

setup(ext_modules=cythonize(exts))
""")


def get_restrain_rts():
    restrain_rts = Path(RESTRAIN_CONFIG.cython.rts).expanduser()
    restrain_include = Path(restrain_rts / "include")
    restrain_lib = Path(restrain_rts / "lib")
    return restrain_include, restrain_lib


def get_includes_and_libs(extra_libs=()):
    restrain_include, restrain_lib = get_restrain_rts()
    return dict(
        include_dirs=[str(restrain_include), *include_paths],
        library_dirs=[str(restrain_lib)],
        libraries=[':typeint', *extra_libs])


def compile_module(mod_name: str, source_code: str, libs=()):
    # TODO:
    # tempfile.TemporaryDirectory will close unexpectedly before removing the generated module.
    # Since that we don't delete the temporary dir as a workaround.

    mod_name = 'RestrainJIT_' + mod_name

    dirname = tempfile.mkdtemp()
    mod_path = mod_name + '.pyx'
    with open(os.path.join(dirname, mod_path), 'w') as pyx_file, open(
            os.path.join(dirname, 'setup.py'), 'w') as setup_file:
        pyx_file.write(source_code)

        setup_file.write(
            template.substitute(
                module=repr(mod_name),
                module_path=repr(mod_path),
                **get_includes_and_libs()))

    cwd = os.getcwd()
    try:
        os.chdir(dirname)

        args = ['setup.py', 'build_ext', '--inplace']
        c = exec_cc(sys.executable, args)

        hd = next(c)
        if hd is not 0:
            sys.stderr.buffer.write(b''.join(c))
            raise RuntimeError("Cython compiler failed.")

        # find the python extension module.
        pyd_name = next(
            each for each in os.listdir(dirname)
            if each.endswith(suffix))
    finally:
        os.chdir(cwd)

    spec = util.spec_from_file_location(mod_name,
                                        os.path.join(dirname, pyd_name))
    mod = util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def setup_pyx_for_cpp():
    """
    This is to support --cplus for pyximport
    """
    import pyximport

    old_get_distutils_extension = pyximport.pyximport.get_distutils_extension

    def new_get_distutils_extension(modname,
                                    pyxfilename,
                                    language_level=None):
        extension_mod, setup_args = old_get_distutils_extension(
            modname, pyxfilename, language_level)
        extension_mod.language = 'c++'
        for k, v in get_includes_and_libs().items():
            setattr(extension_mod, k, v)
        return extension_mod, setup_args

    pyximport.pyximport.get_distutils_extension = new_get_distutils_extension
