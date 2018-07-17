from abc import ABCMeta

import pandas as pd
from pandas.core.generic import PandasMeta
import numpy as np

from .pandas_monkey import patch_arith_methods, get_init_args


class ZMeta(PandasMeta):
    """
    """

    def __new__(cls, name, bases, dct):
        klass = super().__new__(cls, name, bases, dct)
        _pandas_type = klass._pandas_type
        _pandas_type.register(klass)

        klass._init_args = get_init_args(_pandas_type)

        def _wrap_method(cls, _meth_name):
            # this is used for function definitions used by the metaclass.
            # we have no self
            def _meth(self, *args, **kwargs):
                return self._delegate(_meth_name, *args, **kwargs)
            return _meth

        patch_arith_methods(klass, _pandas_type, _wrap_method)
        return klass


class Wrapped(object):
    """
    A wrapped attribute that will currently delegate method call
    and properly pass through getitem/setitem. This is to support
    Indexers (.ix,.iloc) which are both callable and subscriptable
    """

    def __init__(self, obj, attr):
        self.obj = obj
        self.attr = attr

    def __call__(self, *args, **kwargs):
        return _wrapped_method(self.obj, self.attr, *args, **kwargs)

    def __getitem__(self, key):
        return self.obj.pget(self.attr)[key]

    def __setitem__(self, key, val):
        getattr(self.obj, attr)[key] = val


class ZFrame(object, metaclass=ZMeta):

    _pandas_type = pd.DataFrame

    def __init__(self, data, *args, **kwargs):
        self.obj = self._create_pandas_object(data, *args, **kwargs)

    def _create_pandas_object(self, data, *args, **kwargs):
        # only pass the kwargs that pandas want
        pandas_kwargs = {k:v for k, v in kwargs.items() if k in self._init_args}
        obj = self._pandas_type(data, *args, **pandas_kwargs)
        return obj

    def __getattr__(self, name):
        if hasattr(self.obj, name):
            return self._wrap(name)
        raise AttributeError('Meth not found: {meth}'.format(meth=meth))

    def __repr__(self):
        return repr(self.obj)

    def _wrap(self, meth):
        """
        Wrap methods so they passthrough to pandas object
        """
        def func(*args, **kwargs):
            return self._delegate(meth, *args, **kwargs)
        return func

    def _delegate(self, _attr_name, *args, **kwargs):
        """
        Parameters
        ----------
        name : string
            name of attr found on self.pobj
        *args, **kwargs
            optional args that are passed along to method call

        Grab attr of self.pobj. If callable, call immeidately.
        Then we box the output into the original type.

        This is so things like

        >>> res = subclass_df.tail(10)
        >>> assert type(res) == type(subclass_df)

        are True. This is to address the big annoyance where you lose
        the class type when calling methods or attrs.

        Note:
            This has the side affect that if you monkey patch a method or property onto
            Series/DataFrame, this will autobox the results into the original class.
            This is intended
        """
        attr = getattr(self.obj, _attr_name)
        res = attr
        if callable(attr):
            res = attr(*args, **kwargs)
        return self._box_results(res)

    def _box_results(self, res):
        # should just add pandas_types so UserSeries can have two panda types
        if isinstance(res, type(self)._pandas_type) and  \
            type(res) in [pd.DataFrame, pd.Series, pd.TimeSeries]:
            meta = self.obj.__dict__
            # pass in meta as kwargs in case init requires them
            # this assumes that init arg and member name will
            # always be the same. i.e. self.bob = bob
            # make sure to not init args the same name as
            # pandas constructor arguments
            res = type(self)(res, **meta)
            # transfer metadata
            new_dict = res.__dict__
            for k in meta.keys():
                if k == 'obj':
                    continue
                new_dict[k] = meta[k]
        return res
