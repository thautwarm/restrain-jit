[![What's CPython Compat](https://img.shields.io/badge/Hyping-What's&nbsp;"CPython&nbsp;Compatible"-Orange.svg?style=flat)](docs/What-is-CPython-Compatible.md)

## Python Restrain JIT

[![赞助/Donotion](https://img.shields.io/badge/Donation-赞助-Teal.svg?style=flat)](docs/DonationPrivacy.md)
[![开始参与开发/Dev Guide](https://img.shields.io/badge/Start&nbsp;Devel-开发参与指南-Purple.svg?style=flat)](docs/GetStarted.md)


The first and yet the only "CPython compatible" Python JIT, over the world.

This comes with my talk on PyConChina 2019.



After all, "CPython Compatible" means it's not a crispy experimental project.


# 预览

![p1](https://raw.githubusercontent.com/thautwarm/restrain-jit/master/static/p1.png)
![p2](https://raw.githubusercontent.com/thautwarm/restrain-jit/master/static/p2.png)
![p3](https://raw.githubusercontent.com/thautwarm/restrain-jit/master/static/p3.png)

# 原理

![procedure](https://raw.githubusercontent.com/thautwarm/restrain-jit/master/static/procedure.png)

1. Python字节码

    - 字节码指令: [restrain_jit.abs_compiler.instrnames](https://github.com/thautwarm/restrain-jit/blob/master/restrain_jit/abs_compiler/instrnames.py)
    - 字节码处理依赖: [vstinner/bytecode](https://github.com/vstinner/bytecode)

2. 抽象机器代码定义: [restrain_jit.vm.am](https://github.com/thautwarm/restrain-jit/blob/master/restrain_jit/vm/am.py#L23)

3. 抽象指令: `class AM`的interface methods

   其中和具体指令乃至后端无关的intrinsics: [restrain_jit.abs_compiler.py_apis](https://github.com/thautwarm/restrain-jit/blob/master/restrain_jit/abs_compiler/py_apis.py)

4. [抽象解释代码实现](https://github.com/thautwarm/restrain-jit/tree/master/restrain_jit/abs_compiler/from_bc.py)

   利用抽象指令和intrinsics, 以monad方式解耦规定语义的抽象机器和具体的虚拟指令集.

5. [JuVM虚拟栈机](https://github.com/thautwarm/restrain-jit/blob/master/restrain_jit/bejulia/julia_vm.py#37), 前述抽象机器的一个实现.

6. Julia栈机指令: [Python 端](https://github.com/thautwarm/restrain-jit/blob/master/restrain_jit/bejulia/instructions.py), [Julia端](https://github.com/thautwarm/RestrainJIT.jl/blob/master/src/instr_repr.jl).

7. [Monad真好用, 全自动](https://github.com/thautwarm/restrain-jit/blob/master/restrain_jit/vm/am.py#L267)

8. [栈机指令到Julia的代码生成](https://github.com/thautwarm/RestrainJIT.jl/blob/master/src/codegen.jl#L334), pattern matching真好用

9. [Julia "生成函数"](https://docs.juliacn.com/latest/manual/metaprogramming/#%E7%94%9F%E6%88%90%E5%87%BD%E6%95%B0-1), 一种仅仅存在于multistage语言里, 在运行时创建无开销的函数的技巧

10. Type level encoding技巧, 使得创建生成函数像eval一样灵活, 却比静态定义还快.

    - [GG.jl](https://github.com/thautwarm/GeneralizedGenerated.jl)
    - [RestrainJIT.jl/src/runtime_funcs.jl](https://github.com/thautwarm/RestrainJIT.jl/blob/master/src/runtime_funcs.jl)
    - [RestrainJIT.jl/src/typeable.jl](https://github.com/thautwarm/RestrainJIT.jl/blob/master/src/typeable.jl)

11. Python JIT包装, 在函数中添加属性`__jit__`以指示已经jit过的函数

12. PyCall.jl, 包装Pythin JIT函数的途径:

    - [Bridge: Julia to Python](https://github.com/thautwarm/RestrainJIT.jl/blob/master/src/codegen.jl#L303)
    - [Bridge: Python to Julia # 1](https://github.com/thautwarm/restrain-jit/blob/master/restrain_jit/bejulia/jl_protocol.py#L5)
    - [Bridge: Python to Julia # 2](https://github.com/thautwarm/restrain-jit/blob/master/restrain_jit/bejulia/jl_init.py#L32)


# Status

1. intrinsics还远没有实现完, 目前只实现了`py_add`和`py_next`, `py_iter`等.

   **其实现直接简单, 很适合开PR贡献**: 对照[py_apis.py](https://github.com/thautwarm/restrain-jit/blob/master/restrain_jit/abs_compiler/py_apis.py)
   在[py_apis.jl](https://github.com/thautwarm/RestrainJIT.jl/blob/master/src/py_apis.jl)中给出实现.

   P.S: 如果尽可能使用C API压榨性能, 甚至可以对CPython数据结构上的操作进行加速, 见 [Issue 1](https://github.com/thautwarm/restrain-jit/issues/1).

   C API使用可以参考CPython: [cpython/Python/ceval.c](https://github.com/python/cpython/blob/master/Python/ceval.c)


2. 部分语言特性还没实现, 例如生成器, 异步, Python函数调用对关键字参数, 可变位置参数, 可变关键参数的支持.

   其中生成器的实现比较简单直接, 但异步相对来说较难(因为语义来自Python字节码).

   可变关键字参数的实现暂无高效实现.

3. Julia对于代码生成上模拟的Push Pop行为优化不足, 这导致Restrain JIT中的for-loop很慢.
   但是, 我们提供了`restrain_jit.bejulia.functional`模块, 导出了两个函数`foreach`和`select`,
   足以用函数的方式替代控制流, 将避免性能损失.

   另外,
   - 并不复杂的的if-else不会导致性能损失.
   - 由于Julia的错误处理有开销, try语句性能较差(try语句还未经过测试)

4. 因为是Python中文社区, 所以使用中文书写README. 轻喷.

5. 由于依赖PyJulia的原因, 目前只能在dynamically linked的Python(例如anaconda Python, ubuntu源里的Python; Arch Linux的Python是dyn的)下使用.

   但这个限制是没有必要的, 在项目比较成熟时, 会移除PyJulia, 并使用一种前面提到的Bridging技巧, 来消除这个限制.