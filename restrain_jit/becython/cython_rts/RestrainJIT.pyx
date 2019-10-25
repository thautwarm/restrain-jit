#distutils: language=c++
#cython: language_level=3
from libc.stdint cimport int64_t, int32_t, int16_t, int8_t, uint64_t
from libcpp.map cimport map as std_map
from libcpp.string cimport string
from cython.operator cimport dereference

cdef std_map[string, int64_t] internedstrings = std_map[string, int64_t]()

cdef int64_t get_symbol(string s):
    k = internedstrings.find(s)
    if k != internedstrings.end():
        return dereference(k).second
    cdef uint64_t i = internedstrings.size()
    internedstrings[s] = i
    return i

cdef class Cell:
    def __init__(self, x):
        self.cell_contents = x

    def get(self):
        return self.cell_contents

    def set(self, value):
        self.cell_contents = value

cdef object deref_cell(Cell cell):
    return cell.cell_contents

cdef void setref_cell(Cell cell, object o):
    cell.cell_contents = o

cdef inline py_add(NumOrObj1 o1, NumOrObj2 o2):
    return o1 + o2
