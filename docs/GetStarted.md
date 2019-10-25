# Getting Started With Development


## Prerequisite
- Python: CPython 3.6 or newer
- Cython: recommend 0.29+(tested)

## `.restrain` Dotfiles

Copy https://github.com/thautwarm/restrain-jit/tree/master/.restrain to
your user directory, and edit `~/.restrain/info.json`, to specify 
`"cython.rts"`.

```json
{
    "julia": {/*whatever*/},
    "cython": {
        "rts": "~/.restrain/cython_rts"
    }
}
```

Then use `g++`(a C++ compiler compatible to that compiles your Python) to generate necessary libraries.

```
~/.restrain > cd cython_rts/src
~/.restrain/cython_rts/src > g++ -I../include -fPIC -c typeint.c
~/.restrain/cython_rts/src > mv typeint.o ../lib/typeint
```


Then check [tests/becy](https://github.com/thautwarm/restrain-jit/tree/master/tests/becy) for examples, e.g.,

- [Loop](https://github.com/thautwarm/restrain-jit/blob/master/tests/becy/test_loop.py)
- [If](https://github.com/thautwarm/restrain-jit/blob/master/tests/becy/test_if.py)
