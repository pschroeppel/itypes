#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

from .registry import _instantiate_variable

from .float import _FloatVariable
from .flow import _FlowVariable
from .image import _ImageVariable
from .text import _TextVariable
from .props import _PropertiesVariable
from .float_scalar import _FloatScalarVariable