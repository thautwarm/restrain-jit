from cython cimport fused_type
from libc.stdint cimport int64_t, int32_t, int16_t, int8_t, uint64_t
from libcpp.map cimport map as std_map
from libcpp.string cimport string

Num = fused_type(int, float)
cpdef num_func(Num x)
cdef std_map[string, int64_t] internedstrings
cdef int64_t get_symbol(string)