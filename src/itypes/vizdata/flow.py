#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

from ._persistent import _Persistent
from ._persistent_props import _PersistentProperties


class FlowVisualizationData:
    def __init__(self, flow, props=None, label_mask=None, var_id=None):
        self._flow = _Persistent(flow)
        self._props = _PersistentProperties(props)
        self._label_mask = _Persistent(label_mask, dims="hwc")
        self._var_id = var_id

    def var_id(self):
        return self._var_id

    def props(self):
        return self._props

    def flow(self):
        return self._flow

    def label_mask(self):
        return self._label_mask

    def reload(self):
        self._flow.reload()
        self._props.reload()
        self._label_mask.reload()