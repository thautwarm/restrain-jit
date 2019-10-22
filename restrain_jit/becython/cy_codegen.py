from restrain_jit.becython.phi_vm import *
from io import StringIO


class CodeGenOptions:
    # FIXME
    pass


class CodeEmitter:
    lineno_name = "__restrain_mangled_lineno"

    def __init__(self, io: StringIO, options: CodeGenOptions):
        self.prefix = ""
        write = io.write

        def emit_line(line):
            write(line)
            write('\n')

        def change_io_target(new_io: StringIO):
            emit_line.__closure__[0].cell_contents = new_io.write

        self.emit_line = emit_line
        self.change_io_target = change_io_target


def set_lineno(self: CodeEmitter, n: SetLineno):
    code = "{}{} = {}".format(self.prefix, self.lineno_name, n.lineno)
    self.emit_line(code)


def label(self: CodeEmitter, n: Label):
    n.label
