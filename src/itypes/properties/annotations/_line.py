#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

from .registry import register_annotation
from ._annotation import _Annotation


class _LineAnnotation(_Annotation):
    def __init__(self, props, path):
        super().__init__("line", props, path)

    def create(self, x0, y0, x1, y1, **kwargs):
        self._set("x0", x0)
        self._set("y0", y0)
        self._set("x1", x1)
        self._set("y1", y1)

        if "color" in kwargs: self.set_color(kwargs.pop("color"))
        if "alpha" in kwargs: self._set("alpha", kwargs.pop("alpha"))
        if "ls" in kwargs: self.set_ls(kwargs.pop("ls"))
        if "lw" in kwargs: self.set_lw(kwargs.pop("lw"))

        kwargs.pop("shape", None)
        kwargs.pop("size", None)

        if len(kwargs):
            raise Exception(f"don't know how to process arguments {list(kwargs.keys())}")

    def paint(self, painter):
        self._set_pen(painter)
        x0 = self._get("x0")
        y0 = self._get("y0")
        x1 = self._get("x1")
        y1 = self._get("y1")
        painter.drawLine(x0, y0, x1, y1)

register_annotation("line", _LineAnnotation)