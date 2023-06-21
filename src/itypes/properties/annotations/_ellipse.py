#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

from .registry import register_annotation
from ._annotation import _Annotation
import math


class _EllipseAnnotation(_Annotation):
    def __init__(self, props, path):
        super().__init__("ellipse", props, path)

    def create(self, x, y, r0, r1, **kwargs):
        self._set("x", x)
        self._set("y", y)
        self._set("r0", r0)
        self._set("r1", r1)

        if "color" in kwargs: self.set_color(kwargs.pop("color"))
        if "alpha" in kwargs: self._set("alpha", kwargs.pop("alpha"))
        if "a" in kwargs: self._set("a", kwargs.pop("a"))
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
        r0 = self._get("r0")
        r1 = self._get("r1")
        a = self._get("a", 0)

        from PyQt5.QtCore import QRect
        painter.save()
        painter.translate(x, y)
        painter.rotate(a / math.pi * 180)
        rect = QRect(-r0, -r1, 2*r0, 2*r1)
        painter.drawEllipse(rect)
        painter.restore()

register_annotation("ellipse", _EllipseAnnotation)