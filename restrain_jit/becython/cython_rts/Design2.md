
# Deps

```cython
cimport restrain_jit.becython.cython_rts.RestrainJIT as RestrainJIT
from restrain_jit.becython.cython_rts.hotspot cimport pytoint, inttoptr
from libc.stdint cimport uint64_t, int64_t, int32_t, int16_t, int8_t
from libcpp.map cimport map as std_map
from libcpp.vector cimport vector as std_vector
from libcpp.cast cimport static_cast, reinterpret_cast
from cython cimport typeof
```

# Functions

A JITed function is a `cdef class`, each call has a overhead of method lookup.

The methods can be registered dynamically, thus re-compilation don't need to renew all stuffs.


Given this example

```python
def f(x, y, z):
    return x + y + z
```

translates to

```cython
# method type
ctypedef object (*method_t)(object, object, object)

# method lookup type
ctypedef method_t (*method_get_t)(int64_t, int64_t, int64_t)

# method look up ptr
cdef method_get_t method_get = get_method

# to avoid params have conflicts against 'type'
cdef inline method_t __invoke_method_get(x, y, z):
    func = method_get(pytoint(type(x)), pytoint(type(y)), pytoint(type(x)))
    return func

cdef class ty_f:
    # python compatible method to change 'method look up ptr'
    cpdef mut_method_get(self, int64_t f):
        global method_get
        method_get = reinterpret_cast[method_get_t](inttoptr(f))
    def __call__(self, x, y, z):
        """
        '_func__manglexxxx' and '__invoke_method_get'
        should not conflict against the prospective argument name.
        """
        _func__manglexxxx = __invoke_method_get(x, y, z)
        return _func__manglexxxx(x, y, z)
```
