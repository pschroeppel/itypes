#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

from PyQt5.QtGui import QFont

from .registry import register_annotation
from ._annotation import _Annotation
from ...type import is_number



class _TextAnnotation(_Annotation):
    def __init__(self, props, path):
        super().__init__("text", props, path)

    def set_size(self, size):
        if not is_number(size):
            raise Exception(f"invalid size: {size}")
        if size<1 or size>100:
            raise Exception(f"invalid size: {size}")
        self._set("size", size)

    def set_halign(self, value):
        if value not in ["left", "center", "right"]:
            raise Exception(f"invalid value for halign: {value}")
        self._set("halign", value)

    def set_valign(self, value):
        if value not in ["bottom", "center", "top"]:
            raise Exception(f"invalid value for valign: {value}")
        self._set("valign", value)

    def create(self, x, y, text, **kwargs):
        self._set("x", x)
        self._set("y", y)
        self._set("text", text)

        if "color" in kwargs: self.set_color(kwargs.pop("color"))
        if "alpha" in kwargs: self._set("alpha", kwargs.pop("alpha"))
        if "size" in kwargs: self.set_size(kwargs.pop("size"))
        if "halign" in kwargs: self.set_halign(kwargs.pop("halign"))
        if "valign" in kwargs: self.set_valign(kwargs.pop("valign"))

        kwargs.pop("ls", None)
        kwargs.pop("lw", None)
        kwargs.pop("shape", None)

        if len(kwargs):
            raise Exception(f"don't know how to process arguments {list(kwargs.keys())}")

    def paint(self, painter):
        self._set_pen(painter)
        x = self._get("x")
        y = self._get("y")
        text = self._get("text")
        size = max(self._get("size", 12) * painter.scale_coeff, 1)
        halign = self._get("halign", "left")
        valign = self._get("valign", "top")

        from PyQt5.QtCore import QRect, Qt
        rect = QRect(x, y, 0, 0)

        flags = Qt.TextDontClip
        if halign == "left": flags |= Qt.AlignLeft
        if halign == "center": flags |= Qt.AlignHCenter
        if halign == "right": flags |= Qt.AlignRight
        if valign == "top": flags |= Qt.AlignTop
        if valign == "center": flags |= Qt.AlignVCenter
        if valign == "bottom": flags |= Qt.AlignBottom

        font = painter.font()
        font.setPointSizeF(size)
        painter.setFont(font)

        painter.drawText(rect, flags, text)

register_annotation("text", _TextAnnotation)