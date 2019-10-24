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

cdef class JITCounter:
    def __init__(self, dict argtypes_count, times=0):
        self.argtypes_count = argtypes_count
        self.times = 0

    def __getitem__(self, object i):
        v = self.argtypes_count.get(i, 0)
        if v == 0:
            self.argtypes_count[i] = 0
        return v

    def __setitem__(self, object i, object v):
        self.times += 1
        self.argtypes_count[i] = v

    cpdef get_times(self):
        return self.times

    cpdef dict get(self):
        return self.argtypes_count
