from libcpp.map cimport map as std_map
from libcpp.vector cimport vector as std_vector
from libc.stdint cimport int64_t, int32_t, int16_t, int8_t
from cpython.ref cimport PyObject

ctypedef std_map[int64_t, int64_t] hotspot_argument
ctypedef std_map[int16_t, hotspot_argument] hotspot_call
ctypedef std_map[std_vector[int64_t], int8_t] hotspot_jited
ctypedef std_map[std_vector[int64_t], PyObject*] jit_methods

cdef class JITMonitor:
    cdef hotspot_call stats
    cdef hotspot_jited jited
    cdef int16_t argc
    cpdef record(self, std_vector[int64_t])
    cpdef is_generate(self, std_vector[int64_t])
    cpdef generate(self, std_vector[int64_t])
    cpdef search_arg_stats(self, int16_t)
    cpdef search_arg_type_stats(self, int16_t, int64_t)


cdef class JITCounter:
    cdef dict argtypes_count
    cdef int64_t times
    cpdef dict get(self)
    cpdef get_times(self)

cdef extern from "typeint.h":
    object inttopy "inttoptr"(int64_t)
    void* inttoptr(int64_t)
    int64_t pytoint "ptrtoint"(object)
    int64_t ptrtoint(void*)
    int check_ptr_eq(object, object)
    object unsafe_cast(void*)

cpdef int64_t typeid(object)