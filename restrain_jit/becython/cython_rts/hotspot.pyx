#distutils: language=c++
#cython: language_level=3

cdef int64_t typeid(object x):
    return pytoint(type(x))
