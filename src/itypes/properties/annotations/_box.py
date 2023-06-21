#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

from .registry import register_annotation
from ._annotation import _Annotation
from ...type import is_number


class _BoxAnnotation(_Annotation):
    def __init__(self, props, path):
        super().__init__("box", props, path)

    def set_size(self, size):
        if not is_number(size):
            raise Exception(f"invalid size: {size}")
        if size<1 or size>100:
            raise Exception(f"invalid size: {size}")
        self._set("size", size)

    def create(self, x0, y0, x1, y1, **kwargs):
        self._set("x0", x0)
        self._set("y0", y0)
        self._set("x1", x1)
        self._set("y1", y1)

        if "color" in kwargs: self.set_color(kwargs.pop("color"))
        if "alpha" in kwargs: self._set("alpha", kwargs.pop("alpha"))
        if "text" in kwargs: self._set("text", kwargs.pop("text"))
        if "size" in kwargs: self.set_size(kwargs.pop("size"))
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
        text = self._get("text")
        size = max(self._get("size", 12) * painter.scale_coeff, 1)
        painter.drawRect(x0, y0, x1 - x0 + 1, y1 - y0 + 1)

        from PyQt5.QtCore import QRect, Qt
        rect = QRect(x1, y1, 0, 0)

        flags = Qt.TextDontClip
        flags |= Qt.AlignRight
        flags |= Qt.AlignTop

        font = painter.font()
        font.setPointSizeF(size)
        painter.setFont(font)

        painter.drawText(rect, flags, text)

register_annotation("box", _BoxAnnotation)