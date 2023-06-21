#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

from ._file_variable import _FileVariable
from .registry import register_variable


class _FlowVariable(_FileVariable):
    def extension(self): return "flo"

register_variable("flow", _FlowVariable)