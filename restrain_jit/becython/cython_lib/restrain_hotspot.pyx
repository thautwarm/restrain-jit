#distutils: language=c++
#cython: language_level=3

cdef class JITMonitor:
    def __init__(self, int16_t argc):
        self.stats = hotspot_call()
        jited = hotspot_jited()
        self.argc = argc
        for i in range(argc):
            self.stats[i] = hotspot_argument()

    cpdef record(self, std_vector[int64_t] typeids_of_params):
        n = typeids_of_params.size()
        assert n == self.argc
        stats = &self.stats
        for i in range(n):
            m = &(stats[0][i])
            typeid_of_param = typeids_of_params[i]
            if m[0].count(typeid_of_param) == 0:
                m[0][typeid_of_param] = 1
            else:
                m[0][typeid_of_param] += 1

    cpdef is_generate(self, std_vector[int64_t] method):
        return self.jited[method]

    cpdef generate(self, std_vector[int64_t] method):
        self.jited[method] = 1

    cpdef search_arg_stats(self, int16_t argi):
        return self.stats[argi]

    cpdef search_arg_type_stats(self, int16_t argi, int64_t typeid):
        return self.stats[argi][typeid]
