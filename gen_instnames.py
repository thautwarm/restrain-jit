import opcode

with open("restrain_jit/ir/instrnames.py", 'w') as f:
    for k in opcode.opmap:
        f.write(f"{k} = {k!r}\n")
