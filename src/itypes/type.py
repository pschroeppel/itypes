#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

from numpy import uint8
from numpy import uint16
from numpy import float32
from numpy import float64
from numpy import bool

class FAIL:
    pass

class FormattedFloat(float):
    def __new__(self, value, precision):
        return super().__new__(self, value)

    def precision(self):
        return self._precision

    def __init__(self, value, precision):
        super().__init__()
        self._precision = precision

    def __str__(self):
        return f'{self:.{self._precision}f}'

def addr(x):
    if x is None:
        return None
    return hex(id(x))

def is_number(x):
    return isinstance(x, int) or isinstance(x, float)

def is_list(x):
    if isinstance(x, tuple) or isinstance(x, list):
        return True

def is_dict(x):
    if isinstance(x, dict):
        return True

def is_value(x):
    return (not is_list(x)) and (not is_dict(x))

def is_function(x):
    return callable(x)

def ensure_list(x):
    if not is_list(x):
        return [x]
    return x

def is_numpy(x):
    import numpy as np
    return isinstance(x, np.ndarray)

def is_torch(x):
    # We avoid importing torch as it's optional to be installed
    if (x.__class__.__module__, x.__class__.__name__) == ("torch", "Tensor"):
        return True
    return False

def is_struct(x):
    from .struct import Struct
    if isinstance(x, Struct):
        return True

def is_number(x):
    if isinstance(x, int) or isinstance(x, float):
        return True
    return False

def is_str(x):
    return isinstance(x, str)

def is_torch_struct(x):
    from .struct import TorchStruct
    if isinstance(x, TorchStruct):
        return True

def clamp(num, min_value, max_value):
   return max(min(num, max_value), min_value)

def bind_to_instance(instance, func, as_name=None):
    """
    Bind the function *func* to *instance*, with either provided name *as_name*
    or the existing name of *func*. The provided *func* should accept the
    instance as the first argument, i.e. "self".
    """
    if as_name is None:
        as_name = func.__name__
    bound_method = func.__get__(instance, instance.__class__)
    setattr(instance, as_name, bound_method)
    return bound_method

