#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

from .registry import register_visualization
from ...vizdata import TextVisualizationData
from ._single_variable import _SingleVariableVisualization


class _TextVisualization(_SingleVariableVisualization):
    def create(self,
               type,
               index,
               var=None,
               id=None,
               colspan=None,
               rowspan=None,
               text=None,
               width=None,
               height=None,
               valign=None,
               halign=None,
               template=None):
        super().create(type, var, index, id, colspan, rowspan)

        if text is not None: self._set("text", text)
        if width is not None: self._set("width", width)
        if height is not None: self._set("height", height)
        if valign is not None: self._set("valign", valign)
        if halign is not None: self._set("halign", halign)
        if template is not None: self._set("template", template)

    def data(self, group_name, item_name):
        if self._path + "var" not in self._reg:
            return None
        variable_name = self._get("var")
        if (group_name, item_name) not in self._ds.var[variable_name]:
            return None
        value = self._ds.var[variable_name][group_name, item_name]
        file = value.file()

        return TextVisualizationData(file)

    def create_display(self, manager):
        text = ""
        if self._path + "text" in self._reg:
            text = self._get("text")

        from iviz.widgets.displays import TextDisplay
        return TextDisplay(manager,
               text=text,
               id=self._id,
               label=self._get("label"),
               width=self._get("width"),
               height=self._get("height"),
               valign=self._get("valign"),
               halign=self._get("halign"),
               template=self._get("template")
        )


register_visualization("text", _TextVisualization)
