#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

from ._persistent import _Persistent
from ._persistent_props import _PersistentProperties


class ImageVisualizationData:
    def __init__(self, image, props=None, label_mask=None, disp_fields=None, var_id=None):
        self._image = _Persistent(image, dims="hwc")
        self._props = _PersistentProperties(props)
        self._label_mask = _Persistent(label_mask, dims="hwc")
        if disp_fields is None:
            disp_fields = {}
        self._disp_fields = {}
        for name, field in disp_fields:
            self._disp_fields[name] = _Persistent(field)
        self._var_id = var_id

    def var_id(self):
        return self._var_id

    def image(self):
        return self._image

    def props(self):
        return self._props

    def label_mask(self):
        return self._label_mask

    def disp_fields(self):
        return self._disp_fields

    def reload(self):
        self._image.reload()
        self._props.reload()
        self._label_mask.reload()
        for field in self._disp_fields.values():
            field.reload()

