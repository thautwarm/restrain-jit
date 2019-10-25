import restrain_jit.cpy_compat
import test_load as a
a.b = 1
print(type(a))
print(a.__py_module__.b)
a.b = 2

print(a.__state_ages__)
