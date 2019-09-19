# Getting Started With Development

> Recommended use python3.x with system version, PyJulia could not support conda (or other python virtual env which use the static link).
>
> PS: PyJulia will be removed later, so you could use any python version in the later version.

## Install dependencies

``` bash
pip3 install -r requirements.txt
```

## PyCall

In Julia Repl Pkg Mode:

``` julia
add PyCall
add https://github.com/thautwarm/RestrainJIT.jl
```

Exit Pkg Mode :

``` julia
using RestrainJIT # pre-compile Restrain JIT
ENV[PYTHON] = "<add your python binary path here>"
using Pkg
Pkg.build(PyCall) # compile PyCall
```

Test Link Success (in julia repl) :

``` julia
using PyCall
math = pyimport("math")
math.sin(math.pi / 4) # returns ≈ 1/√2 = 0.70710678...
```

## PyJulia

``` python
import julia
julia.install()
```

Test if lined successful :

``` python
from julia import Main
# if could import Main Module, linked success.
```

## Run Demo

``` python
python3 test/test_functional.py
```

