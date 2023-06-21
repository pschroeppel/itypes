#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

from .registry import register_visualization

from .flow import _FlowVisualization
from .float import _FloatVisualization
from .image import _ImageVisualization
from .text import _TextVisualization