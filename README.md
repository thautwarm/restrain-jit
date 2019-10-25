
The developement of this project is suspended due to the complexity of managing multi-language dependencies and Python's verbose functional style codebase. We're now working on creating a static compiled programming language [RemuLang](https://github.com/RemuLang) targeting CPython bytecode, and after the available version of RemuLang released
we'll resume the development of Restrain-JIT.


[![What's CPython Compat](https://img.shields.io/badge/Hyping-What's&nbsp;"CPython&nbsp;Compatible"-Orange.svg?style=flat)](docs/What-is-CPython-Compatible.md)

## Python Restrain JIT

[![赞助/Donotion](https://img.shields.io/badge/Donation-赞助-Teal.svg?style=flat)](docs/DonationPrivacy.md)
[![开始参与开发/Dev Guide](https://img.shields.io/badge/Start&nbsp;Devel-开发参与指南-Purple.svg?style=flat)](docs/GetStarted.md)


The first and yet the only "CPython compatible" Python JIT, over the world.

This comes with my talk on PyConChina 2019.

## Restrain JIT: The Cython Back End

For the previous suspending Julia back end, check the branch [julia-backend](https://github.com/thautwarm/restrain-jit/tree/julia-beckend).

Cython is a widely used Python to C compiler, although it's lack of optimizations, it compiles fast,
which greatly reduces the annoyance of JIT overhead.

Currently the Cython back end works for many fundamental Python constructs. The constructs haven't suppported
yet are exceptions(but you can wrap it as a function) and closures(ready to support today).

The Cython back end did much more on the compilation stuffs, like Control Flow Analysis, many kinds of abstract interpretations, SSA conversions and
corresponding passes. One of the most awesome pass is the Phi-Node analysis pass,
which converts the semantics of Stack Virtual Machine to a Register-based Virtual Machine, and generates Phi nodes:
[phi_node_analysis](https://github.com/thautwarm/restrain-jit/blob/master/restrain_jit/becython/phi_node_analysis.py)

Besides, this is still based on Python bytecode, so Restrain JIT on Cython is still free of hack and available in any case.

The developement of Cython back end is a joy. Yes, debugging is so fast that I can make faster developement iterations,
and no need to wait half a minute when I want to re-run codes :)
