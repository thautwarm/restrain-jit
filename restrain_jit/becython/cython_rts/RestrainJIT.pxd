from cython cimport fused_type
from libc.stdint cimport int64_t, int32_t, int16_t, int8_t, uint64_t
from libcpp.map cimport map as std_map
from libcpp.string cimport string

NumOrObj1 = fused_type(short, int, object)
NumOrObj2 = fused_type(short, int, object)

cdef std_map[string, int64_t] internedstrings
cdef int64_t get_symbol(string)


cdef class Cell:
    cdef object cell_contents

cdef object deref_cell(Cell)
cdef void setref_cell(Cell cell, object o)

cdef inline py_add(NumOrObj1 o1, NumOrObj2 o2)
