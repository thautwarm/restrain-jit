import tempfile
import os
import subprocess
from importlib import util
from string import Template

template = Template(r"""
from distutils.core import setup
from Cython.Build import cythonize
setup(ext_modules=cythonize([$module]))
""")


def compile_module(source_code: str, mod_name: str):
    # TODO:
    # tempfile.TemporaryDirectory will close unexpectedly before removing the generated module.
    # Since that we don't delete the temporary dir as a workaround.
    mod_name = 'cythonextension_' + mod_name

    dirname = tempfile.mkdtemp()
    mod_path = mod_name + '.pyx'
    with open(os.path.join(dirname, mod_path), 'w') as pyx_file, open(
            os.path.join(dirname, 'setup.py'), 'w') as setup_file:
        pyx_file.write(source_code)
        setup_file.write(template.substitute(module=repr(mod_path)))

    cwd = os.getcwd()
    os.chdir(dirname)
    subprocess.check_call(['python', 'setup.py', 'build_ext', '--inplace'])
    os.chdir(cwd)
    pyd_name = next(
        each for each in os.listdir(dirname) if each.endswith('.pyd'))
    spec = util.spec_from_file_location(mod_name,
                                        os.path.join(dirname, pyd_name))
    mod = util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

ddf = compile_module("""

struct 

""", "ddf")