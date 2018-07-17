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

