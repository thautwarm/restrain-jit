from setuptools import setup, find_packages
from datetime import datetime
from pathlib import Path

with Path('README.md').open() as readme:
    readme = readme.read()

setup(
    name='restrain-jit',
    version="0.1",
    keywords="JIT, CPython, Optimizations",  # keywords of your project that separated by comma ","
    description="CPython compatible Python JIT",  # a conceise introduction of your project
    long_description=readme,
    long_description_content_type="text/markdown",
    license='mit',
    python_requires='>=3.6.0',
    url='https://github.com/thautwarm/restrain-jit',
    author='thautwarm',
    author_email='twshere@outlook.com',
    packages=find_packages(),
    entry_points={"console_scripts": []},
    # above option specifies commands to be installed,
    # e.g: entry_points={"console_scripts": ["yapypy=yapypy.cmd.compiler"]}
    install_requires=["bytecode"],
    platforms="any",
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    zip_safe=False,
)