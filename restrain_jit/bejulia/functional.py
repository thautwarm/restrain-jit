"""
As a workaround to the lack of optimizations on Julia's stack machine emulation,
we provide some precompile Julia functions to avoid using coontrol flows like
`for` for `try-catch` for they're not sufficiently efficient.
"""


class JitMap:
    __jit__: callable

    def __call__(self, xs):
        return self.__jit__(xs)


select = JitMap()


class JitForeach:
    __jit__: callable

    def __call__(self, xs):
        return self.__jit__(xs)


foreach = JitForeach()


class AsJuliaObject:
    __jit__: callable

    def __matmul__(self, a):
        return self.__jit__(a)


J = AsJuliaObject()


class SIMDMap:
    __jit__: callable

    def __call__(self, a):
        return self.__jit__(a)


simd_select = SIMDMap()


class SIMDForeach:
    __jit__: callable

    def __call__(self, a):
        return self.__jit__(a)


simd_foreach = SIMDForeach()


class Out:
    __jit__: callable

    def __call__(self, a):
        return self.__jit__(a)


out = Out()
