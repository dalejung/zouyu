"""
Two steps.

1.  Defer execution and build computation manifest kind of like blaze.
2.  When the stuff is evaluated, we run the computation through a proxy. 
    The proxy will time the data evluation and store if necessary

Quesiton is how do you arbitrarily build out an expression graph type of
thing. 

Alos, manifest and deferrment are not the same.


"""
from abc import ABCMeta
from itertools import chain

import pandas as pd
from pandas.core.generic import PandasMeta
import numpy as np

from .pandas_monkey import patch_arith_methods, get_init_args
from .frame import ZMeta


def full_method_name(func):
    if isinstance(func, np.ufunc):
        return func.__name__

    return func.__module__ + '.' + func.__name__


class Operation:

    def __init__(self, name):
        if callable(name):
            name = full_method_name(name)
        self.name = name

    def __call__(self, *args, **kwargs):
        inv = Invoked(self, *args, **kwargs)
        return inv

    def __repr__(self):
        return "Operation: {cls}.{name}".format(cls=self.__class__.__name__,
                                       name=self.name)

class Invoked(object):

    def __init__(self, op, *args, **kwargs):
        self.op = op
        self.args = args
        self.kwargs = kwargs

    def __repr__(self):
        args = map(repr, self.args)
        kwargs = map("{0[0]}={0[1]}".format, self.kwargs.items())
        params = ', '.join(chain(args, kwargs))
        return "Invoked: {name}({params})".format(name=self.op.name, params=params)


class ProxyManager:

    def wrap_callable(self, meth):
        def _func(*args, **kwargs):
            return meth()
        return _func


class ProxyFrame(object, metaclass=ZMeta):

    _pandas_type = pd.DataFrame

    def __init__(self, data, *args, **kwargs):
        pass

    def __getattr__(self, name):
        if hasattr(self._pandas_type, name):
            op = Operation(name)
            return self._proxy(op)
        raise AttributeError('name not found: {name}'.format(name=name))

    def __getattribute__(self, name):
        print('__getattribute__', name)
        return object.__getattribute__(self, name)

    def _proxy(self, name, *args, **kwargs):
        return name

    def __array__(self, dtype=None):
        import inspect;
        self.stack = inspect.stack()
        return np.array([1,2])

    def __array_wrap__(self, arr, context=None):
        print('array_wrap', arr, context)
        ufunc, args, _ = context
        return Operation(ufunc)(*args)

    def _delegate(self, _attr_name, *args, **kwargs):
        print(_attr_name)
        return 1

N = 100
data = np.random.randn(N,3)
index = pd.date_range(start="2000", freq="D", periods=N)
df = ProxyFrame(data, columns=['dale', 'bob', 'frank'], index=index)
"""
We are testing not directly wrapping. Seeing what is possible from just
modifying zouyu frame
"""

# we have to defer attrs since they could themselves cause
# computation due to python's dynamicness
attr_check = df.tail
assert isinstance(attr_check, Operation)

# certain numpy functions will work herecertain numpy functions will work here
assert isinstance(np.isnan(df), Invoked)

# this only works cuz numpy delegates to df.sum
assert isinstance(np.sum(df), Invoked)

# vstack doesn't work, not ufunc
#assert isinstance(np.vstack(df), Invoked)
#assert isinstance(np.nansum(df), Invoked)
