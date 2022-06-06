#!/usr/bin/env python3

from ._variable import _Variable
from .registry import register_variable

class _FloatVariable(_Variable):
    def extension(self): return "npz"

register_variable("float", _FloatVariable)