"""
As a workaround to the lack of optimizations on Julia's stack machine emulation,
we provide some precompile Julia functions to avoid using coontrol flows like
`for` for `try-catch` for they're not sufficiently efficient.
"""


class JitMap:
    __jit__: callable

    def __call__(self, xs):
        return self.__jit__(xs)


map = JitMap()


class JitForeach:
    __jit__: callable

    def __call__(self, xs):
        return self.__jit__(xs)


foreach = JitForeach()
