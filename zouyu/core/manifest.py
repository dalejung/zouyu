import pandas as pd
import numpy as np

class ManifestTracker:
    def __init__(self):
        self.calls = []

    def add_call(self, call):
        self.calls.append(call)

class ProxyFrame(object, metaclass=ZMeta):

    _pandas_type = pd.DataFrame

    def __init__(self, data, *args, **kwargs):
        pass

    def __getattr__(self, name):
        print('__getattr__', name)
        if hasattr(self._pandas_type, name):
            op = Operation(name)
            return self._proxy(op)
        raise AttributeError('name not found: {name}'.format(name=name))

    def __getattribute__(self, name):
        print('__getattribute__', name)
        return object.__getattribute__(self, name)

    def _proxy(self, name, *args, **kwargs):
        """
        Parameters
        ----------
        name : string
            name of attr found on self.pobj
        """
        return name

    def __array__(self, dtype=None):
        import inspect
        frames = inspect.getouterframes(inspect.currentframe())
        import ipdb; ipdb.set_trace()
        return np.array([])

    def __array_wrap__(self, arr, context=None):
        print('array_wrap', context)
        ufunc, args, _ = context
        return Operation(ufunc)(*args)

    def _delegate(self, _attr_name, *args, **kwargs):
        pass
