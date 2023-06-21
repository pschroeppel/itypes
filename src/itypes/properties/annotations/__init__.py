#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

from .registry import _instantiate_annotation
from .registry import _reinstantiate_annotation

from ._line import _LineAnnotation
from ._rect import _RectAnnotation
from ._circle import _CircleAnnotation
from ._mark import _MarkAnnotation
from ._text import _TextAnnotation
from ._box import _BoxAnnotation
from ._ellipse import _EllipseAnnotation