import sys
from types import ModuleType
import _heapq as hq
print(sys.modules['_heapq'])
headq = ModuleType('_heapq', hq.__doc__)
headq.__dict__.update(hq.__dict__)
sys.modules['_heapq'] = headq
import _heapq
print(_heapq is headq, _heapq is hq)
# from restrain_jit.bejulia.functional import foreach, select, simd_select, J, out
# from restrain_jit.bejulia.julia_vm import JuVM
from restrain_jit.bejulia.jl_init import init

# import timeit
# import numpy as np
#
# init()
#
# jit = JuVM.func_info
#
#
# @jit
# def all_add2(lst):
#
#     @select(lst)
#     def ret(elt):
#         return elt + 2
#
#     return ret
#
#
# # xs = np.arange(20000)
# # zs = all_add2(xs)
#
#
# @jit
# def const(_):
#     return 5
#
#
# print(type(const))
# print(const(1))
# #
# # def py_all_add2(lst):
# #
# #     # np.fromiter is the most efficient way to
# #     # create numpy array from python iterator
# #     return np.fromiter(
# #         map(lambda x: x + 2, lst), dtype=np.int32, count=len(lst))
# #
# #
# # @jit
# # def all_add2_simd(lst, out):
# #
# #     @simd_select(lst, out)
# #     def ret(elt):
# #         return elt + 2
# #
# #     return ret
# #
# #
# # ret = out(J @ np.ones(len(xs)))
# # print(all_add2_simd(xs, ret))
# #
# # jit_time = timeit.timeit(
# #     """
# # all_add2(xs)""",
# #     globals=dict(all_add2=all_add2, xs=xs),
# #     number=1000)
# #
# # cpy_time = (timeit.timeit(
# #     """
# # all_add2(xs)""",
# #     globals=dict(all_add2=py_all_add2, xs=xs),
# #     number=1000))
# #
# # print(ret)
# #
# # simd_time = (timeit.timeit(
# #     """
# # all_add2(xs, out)""",
# #     globals=dict(all_add2=all_add2_simd, xs=xs, out=ret),
# #     number=1000))
# # print()
# # print(cpy_time)
# # print(jit_time)
# # print(simd_time)
