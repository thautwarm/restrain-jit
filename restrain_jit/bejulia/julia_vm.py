from restrain_jit.bejulia.instructions import *
from restrain_jit.bejulia.representations import *
from restrain_jit.vm.am import AM
import typing as t
from dataclasses import dataclass


@dataclass
class JuVM(AM[Instr, Repr]):

    def pop_exception(self, must: bool) -> Repr:
        name = self.alloc()
        self.add_instr(name, PopException(must))
        return Reg(name)

    def meta(self) -> dict:
        return self._meta

    def last_block_end(self) -> str:
        return self.end_label

    def push_block(self, end_label: str) -> None:
        self.blocks.append((end_label, []))

    def pop_block(self) -> Repr:
        end_label, instrs = self.blocks.pop()
        regname = self.alloc()
        instr = UnwindBlock(instrs)
        self.add_instr(regname, instr)
        return Reg(regname)

    def from_const(self, val: Repr) -> object:
        assert isinstance(val, Const)
        return val.val

    def ret(self, val: Repr):
        return self.add_instr(None, Return(val))

    def const(self, val: object):
        return Const(val)

    @classmethod
    def reg_of(cls, n: str):
        return Reg(n)

    def from_higher(self, qualifier: str, name: str):
        regname = self.alloc()
        self.add_instr(regname, PyGlob(qualifier, name))
        return Reg(regname)

    def from_lower(self, qualifier: str, name: str):
        regname = self.alloc()
        self.add_instr(regname, JlGlob(qualifier, name))
        return Reg(regname)

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
            return self.st[-n - 1]
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

    def release(self, name: Repr):
        """
        release temporary variable
        """
        if not isinstance(name, Reg):
            return
        name = name.n
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

    # meta data
    _meta: dict
    # stack
    st: t.List[Repr]
    # instructions
    blocks: t.List[t.Tuple[t.Optional[str], t.
                           List[t.Tuple[t.Optional[str], Instr]]]]

    # allocated temporary
    used: t.Set[str]
    unused: t.Set[str]

    @property
    def instrs(self):
        return self.blocks[-1][1]

    @property
    def end_label(self) -> t.Optional[str]:
        return self.blocks[-1][0]

    @classmethod
    def pass_push_pop_inline(cls, instrs):
        blacklist = set()
        i = 0
        while True:
            try:
                k, v = instrs[i]
            except IndexError:
                break
            if isinstance(v, UnwindBlock):
                v.instrs = cls.pass_push_pop_inline(v.instrs)
            if k is None and isinstance(v, Pop):
                j = i - 1
                while True:
                    k, v = instrs[j]
                    if k is None and isinstance(v, Push):
                        blacklist.add(j)
                        blacklist.add(i)
                        i += 1
                        j -= 1
                        try:
                            k, v = instrs[i]
                        except IndexError:
                            break
                        if k is None and isinstance(v, Pop):
                            continue
                        break

                    else:
                        i += 1
                        break
            else:
                i = i + 1

        return [
            each for i, each in enumerate(instrs) if i not in blacklist
        ]
