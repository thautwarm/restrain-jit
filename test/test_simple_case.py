from restrain_jit.julia import jit

@jit
def f(arr):
    n = len(arr)
    @parallel_for(arr)
    def apply(refi):
        refi[i] = i + n
    return arr

