RestrainJIT Generated Cython Spec:


# Prelude

```cython
from restrain_jit.becython.cython_rts cimport RestrainJIT
from restrain_jit.becython.cython_rts.hotspot cimport inttopy, pytoint, JITCounter
from libc.stdint cimport int64_t, int32_t, int16_t, int8_t
from libcpp.map cimport map as std_map
from libcpp.vector cimport vector as std_vector
from cython cimport typeof
```


# Functions

A JITed function is represented as a `cpdef` function, whose arguments are typed with cython's fused types,
for instance, given

```python
def f(x, y, z):
    return x + y + z
```

The JIT version(haven't compiled JITed methods) is
```
cdef fused Arg1:
    object

cdef fused Arg2:
    object

cdef fused Arg3:
    object


cdef JITCounter counter
cdef object recompile_handler
cdef object global_abs


cpdef f(Arg1 x, Arg2 y, Arg3 z):
    if typeof(x) == typeof(object) or typeof(x) == typeof(object) or typeof(z) == typeof(object):
        counter[(jittype(x), jittype(y), jittype(z))] += 1
        if counter.times % 100 == 0:
            recompile_handler()

    # the next statement means the fake code.
    # * the actual code will be retrieved from
    #   Python function object(including the bytecode)
    #   and processed by several JIT compiler passes
    return x + y + z

cpdef init(dict globs, dict _counter, _handler):
    global global_abs, counter, recompile_handler
    global_abs = globs['abs']
    counter = JITCounter(_counter)
    recompile_handler = _handler
```

# JIT

When the `recompile_handler` is notified, it'll use the counter to
check which combinations of arguments' types are the hottest used,
and add them to the fused types, and recompile the file and reload them.


e.g, if `f(int, float, int)` is found out to be used the most frequently,
we'll change the definition of fused types,

```
cdef fused Arg1:
    object
    int

cdef fused Arg2:
    object
    float

cdef fused Arg3:
    object
    int
```

The use of fused types could lead to some problems in current stage,
and there's a workaround: https://github.com/cython/cython/issues/3204


# Dependencies of JIT

Sometimes, the type is not the trivial primitive types,
they might be user-defined types.

To support JIT, a type should meet some conditions, and can be translated
into Cython cdef class.

*To be continue*
