from restrain_jit.becython.cy_loader import compile_module
mod = """

"""

mod = compile_module('m', mod)

print(mod.f(14514))
