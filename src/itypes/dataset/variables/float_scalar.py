#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

from ._variable import _Variable
from .registry import register_variable

class _FloatScalarVariable(_Variable):
    pass

register_variable("float-scalar", _FloatScalarVariable)