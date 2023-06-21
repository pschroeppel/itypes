#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

#!/usr/bin/env python3

from .registry import register_annotation
from ...type import is_str, is_list, is_number
from ...json_registry import JsonRegistryNode

_line_styles = {
     'solid':                 None,
     '-':                     None,

     'loosely dotted':        (1, 10),
     'dotted':                (1, 1),
     '.':                     (1, 1),
     'densely dotted':        (1, 1),

     'loosely dashed':        (5, 10),
     'dashed':                (5, 5),
     '--':                    (5, 5),
     'densely dashed':        (5, 1),

     'loosely dashdotted':    (3, 10, 1, 10),
     'dashdotted':            (3, 5, 1, 5),
     '-.':                    (3, 5, 1, 5),
     'densely dashdotted':    (3, 1, 1, 1),

     'dashdotdotted':         (3, 5, 1, 5, 1, 5),
     'loosely dashdotdotted': (3, 10, 1, 10, 1, 10),
     'densely dashdotdotted': (3, 1, 1, 1, 1, 1)
}

class _Annotation(JsonRegistryNode):
    def __init__(self, type, props, path):
        super().__init__(props._reg, path)
        self._props = props

        self._set("type", type)

    def set_color(self, color):
        if is_str(color):
            if color[0] != "#":
                raise Exception(f"don't know how to parse {color}")

            hex_digits = color[1:]
            if len(hex_digits) != 6:
                raise Exception(f"length of hex digits is not six: {color}")

            for hex_digit in hex_digits:
                if hex_digit not in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"]:
                    raise Exception(f"invalid hex code: {color}")
        else:
            raise Exception("invalid color: {color}")

        self._set("color", color)

    def set_ls(self, ls):
        if ls not in _line_styles:
            raise Exception(f"invalid line style: {ls}")
        self._set("ls", ls)

    def set_lw(self, lw):
        if not is_number(lw):
            raise Exception(f"invalid line width: {ls}")
        if lw<0 or lw>100:
            raise Exception(f"invalid line width: {ls}")
        self._set("lw", lw)

    def _set_pen(self, painter):
        from PyQt5.QtGui import QColor, QPen, QBrush

        if self._path + "color" in self._reg:
            color = QColor(self._get("color"))
        else:
            color = QColor("#ffffff")

        if self._path + "alpha" in self._reg:
            color.setAlphaF(self._get("alpha"))

        brush = QBrush(color)

        lw = painter.scale_coeff
        if self._path + "lw" in self._reg:
            lw *= self._get("lw")

        pen = QPen(brush, lw)
        if self._path + "ls" in self._reg:
            pattern = [x / painter.scale_coeff for x in _line_styles[self._reg[self._path + "ls"]]]
            pen.setDashPattern(pattern)

        painter.setPen(pen)
