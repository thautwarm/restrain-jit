from libcpp.map cimport map as std_map
from libcpp.vector cimport vector as std_vector
from libc.stdint cimport int64_t, int32_t, int16_t, int8_t
from cpython.ref cimport PyObject

cdef extern from "typeint.h":
    object inttopy "inttoptr"(int64_t)
    void* inttoptr(int64_t)
    int64_t pytoint "ptrtoint"(object)
    int64_t ptrtoint(void*)
    int check_ptr_eq(object, object)
    object unsafe_cast(void*)

cdef int64_t typeid(object)