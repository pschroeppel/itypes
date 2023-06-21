#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

from ._persistent import _Persistent
from ._persistent_props import _PersistentProperties


class FloatVisualizationData:
    def __init__(self, float, props=None, label_mask=None, var_id=None):
        self._float = _Persistent(float)
        self._props = _PersistentProperties(props)
        self._label_mask = _Persistent(label_mask, dims="hwc")
        self._var_id = var_id

    def var_id(self):
        return self._var_id

    def float(self):
        return self._float

    def props(self):
        return self._props

    def label_mask(self):
        return self._label_mask

    def reload(self):
        self._float.reload()
        self._props.reload()
        self._label_mask.reload()