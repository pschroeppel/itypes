#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

from .registry import register_annotation
from ._annotation import _Annotation


class _CircleAnnotation(_Annotation):
    def __init__(self, props, path):
        super().__init__("circle", props, path)

    def create(self, x, y, r, **kwargs):
        self._set("x", x)
        self._set("y", y)
        self._set("r", r)

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
        x = self._get("x")
        y = self._get("y")
        r = self._get("r")
        from PyQt5.QtCore import QRect
        rect = QRect(x-r, y-r, 2*r, 2*r)
        painter.drawEllipse(rect)

register_annotation("circle", _CircleAnnotation)