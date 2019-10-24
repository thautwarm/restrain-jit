#distutils: language=c++
#cython: language_level=3
from libc.stdint cimport int64_t, int32_t, int16_t, int8_t, uint64_t
from libcpp.map cimport map as std_map
from libcpp.string cimport string
from cython.operator cimport dereference
cpdef num_func(Num x):
    return x + 1

cdef std_map[string, int64_t] internedstrings = std_map[string, int64_t]()

cdef int64_t get_symbol(string s):
    k = internedstrings.find(s)
    if k != internedstrings.end():
        return dereference(k).second
    cdef uint64_t i = internedstrings.size()
    internedstrings[s] = i
    return i
