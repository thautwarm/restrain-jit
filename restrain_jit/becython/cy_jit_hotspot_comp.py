import typing as t
import abc
import numpy as np
from restrain_jit.becython.cy_jit_common import *
from collections import Counter
try:
    from .cy_jit import JITSystem, JITFunctionHoldPlace
except ImportError:
    pass

extension_type_pxd_paths = {
    int: None,
    float: None,
    str: None,
    bytes: None,
    list: None,
    tuple: None,
    dict: None,
    set: None,
    np.ndarray: 'numpy'
}


class Strategy(abc.ABC):

    @abc.abstractmethod
    def __call__(self, calls: call_records_t, freq: Counter, n: int):
        raise NotImplementedError


def is_jit_able_type(t: type):
    return t in extension_type_pxd_paths


class HitN(Strategy):

    def __init__(self, threshold: int):
        self.threshold = threshold

    def __call__(self, _, freq: Counter, n: int):
        threshold = self.threshold
        for k, v in freq.items():
            if v > threshold:
                yield k


class JITRecompilationDecision:

    def __init__(self, strategies: t.Iterable[Strategy]):
        self.strategies = list(strategies)

    def add_rules(self, strategies: t.Iterable[Strategy]):
        self.strategies.extend(strategies)

    def select(self, calls):
        freq = Counter(calls)
        n = len(calls)
        new_jt = set()
        for strategy in self.strategies:
            new_jt.update(strategy(calls, freq, n))
        return new_jt

    def trigger_jit(self, fn_place: 'JITFunctionHoldPlace'):
        call_recorder = fn_place.call_recorder
        new_jt = self.select(call_recorder.get())
        dispatcher = {}
        for argtypeids in new_jt:
            argtypes = tuple(map(call_recorder.load_type, argtypeids))
            dispatcher[argtypeids] = argtypes
        fn_place.add_methods(dispatcher)
