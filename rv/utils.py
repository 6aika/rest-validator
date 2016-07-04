import importlib
import inspect
import sys
import time


class cached_property(object):
    """
    A property that is only computed once per instance and then replaces
    itself with an ordinary attribute. Deleting the attribute resets the
    property.

    Source: https://github.com/bottlepy/bottle/blob/0.11.5/bottle.py#L175
    """

    def __init__(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            # We're being accessed from the class itself, not from an object
            return self
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value


def wallclock():
    """
    Return a number of seconds.

    Useful for benchmarking.

    :return: float
    """
    if sys.platform == 'win32':
        return time.clock()
    else:
        return time.time()


def find_class(classpath, subclass):
    """
    Find a class object of the given type given a dotted string.

    One may pass either a full class such as `rv.tests.base.Test`,
    or a module containing one (in which case the first matching
    class is returned).

    :param classpath: Class path string
    :param subclass: Find a subclass of this class.
    :return: class object or None
    :rtype: object|None
    """
    bits = classpath.split('.')
    if bits[-1][0].isupper():  # Last bit is capitalized; assume it's a classpath
        val = getattr(importlib.import_module('.'.join(bits[:-1])), bits[-1])
        assert issubclass(val, subclass)
        return val
    else:  # Last bit not capitalized; assume it's a module and find the first valid subclass
        mod = importlib.import_module(classpath)
        for var, val in vars(mod).items():
            if inspect.isclass(val) and val is not subclass and issubclass(val, subclass):
                return val
