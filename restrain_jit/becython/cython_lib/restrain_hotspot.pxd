from libcpp.map cimport map as std_map
from libcpp.vector cimport vector as std_vector
from libc.stdint cimport int64_t, int32_t, int16_t, int8_t

ctypedef std_map[int64_t, int64_t] hotspot_argument
ctypedef std_map[int16_t, hotspot_argument] hotspot_call
ctypedef std_map[std_vector[int64_t], int8_t] hotspot_jited

cdef class JITMonitor:
    cpdef void record(self, std_vector[int64_t])
    cpdef int8_t is_generate(self, std_vector[int64_t])
    cpdef void generate(self, std_vector[int64_t])
    cpdef hotspot_argument search_arg_stats(self, int16_t)
    cpdef int64_t search_arg_type_stats(self, int16_t, int64_t)
