from restrain_jit.bejulia.julia_vm import JuVM as jit


@jit
def f(arr):
    n = len(arr)

    @parallel_for(arr)
    def apply(refi):
        refi[i] = i + n

    return arr
