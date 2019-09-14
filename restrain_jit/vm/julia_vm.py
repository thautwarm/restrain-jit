from restrain_jit.ir.instructions import *
from restrain_jit.ir.representations import *
from restrain_jit.vm.am import AM
import typing as t
from dataclasses import dataclass


@dataclass
class VM(AM[Instr, Repr]):
    @classmethod
    def reg_of(cls, n: str):
        return Reg(n)

    def app(self, f: Repr, args: t.List[Repr]) -> Repr:
        name = self.alloc()
        self.add_instr(name, App(f, args))
        return Reg(name)

    def store(self, n: str, val: Repr):
        self.add_instr(None, Store(Reg(n), val))

    def load(self, n: str) -> Repr:
        r = Reg(n)
        name = self.alloc()
        self.add_instr(name, Load(r))
        return Reg(name)

    def assign(self, n: str, v: Repr):
        self.add_instr(None, Ass(Reg(n), v))

    def peek(self, n: int):
        try:
            return self.st[-n]
        except IndexError:
            name = self.alloc()
            self.add_instr(name, Peek(n))
            return name

    def jump(self, n: str):
        self.add_instr(None, Jmp(n))

    def jump_if_push(self, n: str, cond: Repr, leave: Repr):
        self.add_instr(None, JmpIfPush(n, cond, leave))

    def jump_if(self, n: str, cond: Repr):
        self.add_instr(None, JmpIf(n, cond))

    def label(self, n: str) -> None:
        self.add_instr(None, Label(n))

    def push(self, r: Repr) -> None:
        self.st.append(r)
        self.add_instr(None, Push(r))

    def pop(self) -> Repr:
        try:

            a = self.st.pop()
            self.add_instr(None, Pop())
        except IndexError:
            name = self.alloc()
            self.add_instr(name, Pop())
            a = Reg(name)
        return a

    def release(self, name: str):
        """
        release temporary variable
        """
        if name in self.used:
            self.used.remove(name)
            self.unused.add(name)

    def alloc(self):
        """
        allocate a new temporary variable
        """
        if self.unused:
            return self.unused.pop()
        tmp_name = f"tmp-{len(self.used)}"
        self.used.add(tmp_name)
        return tmp_name

    def add_instr(self, tag, instr: Instr):
        self.instrs.append((tag, instr))
        return None

    # stack
    st: t.List[Repr]
    # instructions
    instrs: t.List[t.Tuple[str, Instr]]

    # allocated temporary
    used: t.Set[str]
    unused: t.Set[str]
