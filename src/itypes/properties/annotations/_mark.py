#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

from .registry import register_annotation
from ._annotation import _Annotation
from ...type import is_str, is_list, is_number


def paint_plus(painter, x, y, size):
    r = size / 2
    from PyQt5.QtCore import QLineF
    painter.drawLine(QLineF(x-r, y, x+r, y))
    painter.drawLine(QLineF(x, y-r, x, y+r))

def paint_cross(painter, x, y, size):
    r = size / 2
    from PyQt5.QtCore import QLineF
    painter.drawLine(QLineF(x-r, y-r, x+r, y+r))
    painter.drawLine(QLineF(x-r, y+r, x+r, y-r))

def paint_square(painter, x, y, size):
    r = size / 2
    from PyQt5.QtCore import QRectF
    painter.drawRect(QRectF(x-r, y-r, 2*r, 2*r))

def paint_triangle(painter, x, y, size):
    r = size / 2
    from PyQt5.QtCore import QLineF
    painter.drawLine(QLineF(x-r, y, x, y-r))
    painter.drawLine(QLineF(x+r, y, x, y-r))
    painter.drawLine(QLineF(x-r, y, x+r, y))

def paint_circle(painter, x, y, size):
    r = size / 2
    from PyQt5.QtCore import QRectF
    rect = QRectF(x-r, y-r, 2*r, 2*r)
    painter.drawEllipse(rect)

_shapes = {
    "+": paint_plus,
    "x": paint_cross,
    "s": paint_square,
    "^": paint_triangle,
    "o": paint_circle
}

class _MarkAnnotation(_Annotation):
    def __init__(self, props, path):
        super().__init__("mark", props, path)

    def set_size(self, size):
        if not is_number(size):
            raise Exception(f"invalid size: {size}")
        if size<1 or size>100:
            raise Exception(f"invalid size: {size}")
        self._set("size", size)

    def set_shape(self, shape):
        if shape not in _shapes:
            raise Exception(f"uknown shape {shape}")
        self._set("shape", shape)

    def create(self, x, y, **kwargs):
        self._set("x", x)
        self._set("y", y)

        if "color" in kwargs: self.set_color(kwargs.pop("color"))
        if "alpha" in kwargs: self._set("alpha", kwargs.pop("alpha"))
        if "ls" in kwargs: self.set_ls(kwargs.pop("ls"))
        if "lw" in kwargs: self.set_lw(kwargs.pop("lw"))
        if "shape" in kwargs: self.set_shape(kwargs.pop("shape"))
        if "size" in kwargs: self.set_size(kwargs.pop("size"))

        if len(kwargs):
            raise Exception(f"don't know how to process arguments {list(kwargs.keys())}")

    def paint(self, painter):
        self._set_pen(painter)
        x = self._get("x")
        y = self._get("y")
        shape = self._get("shape", '+')
        size = self._get("size", 5) * painter.scale_coeff
        _shapes[shape](painter, x, y, size)

register_annotation("mark", _MarkAnnotation)