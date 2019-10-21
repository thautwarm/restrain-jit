import tempfile
import os
import platform
import sys
from importlib import util
from string import Template

import Cython.Includes as includes
include_path = list(includes.__path__)

suffix = '.pyd' if platform.system() == 'Windows' else '.so'


def exec_subproc(cmd, args):
    file = cmd
    err_in, err_out = os.pipe()
    if os.fork():
        _, status = os.wait()
        os.close(err_out)
        yield status
        while True:
            load = os.read(err_in, 1024)
            if not load:
                break
            yield load
    else:
        # for child process
        os.close(err_in)
        os.dup2(err_out, sys.stderr.fileno())
        os.execvpe(file, [cmd, *args], dict(os.environ))
        # in case that os.execvp fails
        sys.exit(127)


template = Template(r"""
from distutils.core import setup
from Cython.Build import cythonize
setup(
    ext_modules=cythonize([$module]),
    include_dirs=[$include]
)
""")


def compile_module(mod_name: str, source_code: str):
    # TODO:
    # tempfile.TemporaryDirectory will close unexpectedly before removing the generated module.
    # Since that we don't delete the temporary dir as a workaround.
    mod_name = 'cythonextension_' + mod_name

    dirname = tempfile.mkdtemp()
    mod_path = mod_name + '.pyx'
    with open(os.path.join(dirname, mod_path), 'w') as pyx_file, open(
            os.path.join(dirname, 'setup.py'), 'w') as setup_file:
        pyx_file.write(source_code)
        setup_file.write(
            template.substitute(
                module=repr(mod_path), include=include_path))

    cwd = os.getcwd()
    try:
        os.chdir(dirname)

        c = exec_subproc(sys.executable,
                         ['setup.py', 'build_ext', '--inplace'])

        hd = next(c)
        if hd is not 0:
            sys.stderr.buffer.write(b''.join(c))
            raise SystemError

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

