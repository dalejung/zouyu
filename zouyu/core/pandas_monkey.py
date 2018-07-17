import inspect

import pandas as pd
import pandas.core.ops as ops
from pandas.core.generic import NDFrame

_TYP_MAP = {
    pd.Series : 'series',
    pd.DataFrame : 'frame',
    pd.Panel : 'panel'
}

def get_arith_methods(_typ):
    """
    Because certain magic methods don't get intercepted by __getattribute__,
    we have to explicitly define them on our classes. We use internal pandas
    methods to attach the methods to a Dummy class and grab the names from that.

    Note: Would like to just grab a dict of arith methods, but there doesn't
    seem to be an api for that.

    _typ : String
        series, frame, panel
    """

    class Dummy(object):
        pass

    _flex_funcs = "{_typ}_flex_funcs".format(_typ=_typ)
    ops.add_flex_arithmetic_methods(Dummy, **getattr(ops, _flex_funcs))
    _special_funcs = "{_typ}_special_funcs".format(_typ=_typ)
    ops.add_special_arithmetic_methods(Dummy, **getattr(ops, _special_funcs))

    arith_methods = Dummy.__dict__.keys()
    arith_methods = set(arith_methods)
    arith_methods ^= {'__dict__', '__module__'}

    return arith_methods

def patch_arith_methods(cls, _typ, wrapper):
    if issubclass(_typ, NDFrame):
        _typ = _TYP_MAP.get(_typ)

    assert isinstance(_typ, str)
    arith_methods = get_arith_methods(_typ)
    for meth in arith_methods:
        wrapped = wrapper(cls, meth)
        setattr(cls, meth, wrapped)

def get_init_args(pandas_type):
    init_func = getattr(pandas_type, '__init__')
    argspec = inspect.getargspec(init_func)
    return argspec.args[1:] # skip self
