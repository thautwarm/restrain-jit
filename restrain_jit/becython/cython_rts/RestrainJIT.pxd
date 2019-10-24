from cython cimport fused_type
Num = fused_type(int, float)
cpdef num_func(Num x)
