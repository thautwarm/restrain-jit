# What's "CPython Compatible"

"CPython Compatible" here might not be that proper after a simple glance, but I haven't found out a word for this.

A "CPython Compatible" JIT roughly means:

- Should be able to work with existing and prospective C-extensions of the CPython world.

- Should be able to keep the same semantics bewteen the jitted code and original CPython code.

- Should be able to support JITing most of Python objects(intentionally, everything other than objects from c-extensions, builtin/frozen modules), if specified.

- Should be able to taken advantage as a regular Python 3-rd party library.

Besides, I sometimes want to call it an **available** Python JIT.

**If you get a better word to describe above properties, you could tell us at once, which will be specially appreciated.**
