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
(Mac OSX user please see follow chapter "Fix Build Bug On Mac OSX" )

```
~/.restrain > cd cython_rts/src
~/.restrain/cython_rts/src > g++ -I../include -fPIC -c typeint.c
~/.restrain/cython_rts/src > mv typeint.o ../lib/typeint
```


Then check [tests/becy](https://github.com/thautwarm/restrain-jit/tree/master/tests/becy) for examples, e.g.,

- [Loop](https://github.com/thautwarm/restrain-jit/blob/master/tests/becy/test_loop.py)
- [If](https://github.com/thautwarm/restrain-jit/blob/master/tests/becy/test_if.py)

### Fix Build Bug on Mac OSX
Mac OSX user may encounter `g++` command error like: `ld: library not found for -l:typeint`. 

Use follow command instead: 

```
~/.restrain > cd cython_rts/src
~/.restrain/cython_rts/src > g++ -I../include -fPIC -c typeint.c -o libtypeint.so
~/.restrain/cython_rts/src > mv libtypeint.so ../lib/libtypeint.so
```

Change code in `becython/cy_loader.py` 

```
-- libraries=[':typeint', *extra_libs])
++ libraries=['typeint', *extra_libs])
```
 