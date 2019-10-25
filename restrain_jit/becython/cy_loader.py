import tempfile
import os
import platform
import sys
import pyximport
from importlib import util, import_module
from restrain_jit.config import RESTRAIN_CONFIG
from pathlib import Path
from string import Template
from restrain_jit.utils import exec_cc
try:
    import Cython.Includes as includes
except ImportError:
    raise RuntimeError("For using Cython backend, cython package is required.")
include_paths = list(includes.__path__)

JIT_DATA_DIR = Path(tempfile.TemporaryDirectory(prefix="restrain").name)
JIT_DATA_DIR.mkdir()

JIT_FUNCTION_DIR = JIT_DATA_DIR / "Restrain_paths_functions"
JIT_TYPE_DIR = JIT_DATA_DIR / "Restrain_paths_types"
sys.path.append(str(JIT_DATA_DIR))

JIT_FUNCTION_DIR.mkdir()
JIT_TYPE_DIR.mkdir()
with (JIT_TYPE_DIR / "__init__.py").open('w') as f:
    f.write('# So, this is a module, a cython module!')

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
        language="c++",
        extra_compile_args=["-std=c++11", '-O3'],
        extra_link_args=["-std=c++11", '-O3']
    )
]

setup(
    ext_modules=cythonize(
        exts,
        compiler_directives=dict(language_level="3str", infer_types=True)
    ))
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


def compile_module(under_dir: Path, mod_name: str, source_code: str, libs=()):
    # TODO:
    # tempfile.TemporaryDirectory will close unexpectedly before removing the generated module.
    # Since that we don't delete the temporary dir as a workaround.

    mod_name = mod_name
    dirname = tempfile.mkdtemp(dir=str(under_dir))
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
        # pyd_name = next(each for each in os.listdir(dirname) if each.endswith(suffix))
    finally:
        os.chdir(cwd)

    mod = import_module("{}.{}.{}".format(under_dir.name,
                                          os.path.split(dirname)[1], mod_name))
    return mod


def setup_pyx_for_cpp():
    """
    This is to support --cplus for pyximport
    """

    old_get_distutils_extension = pyximport.pyximport.get_distutils_extension

    def new_get_distutils_extension(modname, pyxfilename, language_level=None):
        extension_mod, setup_args = old_get_distutils_extension(modname, pyxfilename,
                                                                language_level)
        extension_mod.language = 'c++'
        for k, v in get_includes_and_libs().items():
            setattr(extension_mod, k, v)
        return extension_mod, setup_args

    pyximport.pyximport.get_distutils_extension = new_get_distutils_extension


setup_pyx_for_cpp()
pyximport.install()
