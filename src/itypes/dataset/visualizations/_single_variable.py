#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

from ._visualization import _Visualization
from copy import deepcopy


class _SingleVariableVisualization(_Visualization):
    def create(self, type, var, index, id=None, colspan=None, rowspan=None, label=None, props=None):
        if id is None:
            id = var
        if id is None:
            id = type
        self._id = self._ds.viz._new_id(id)
        self._path = self._base_path + self._id

        super().create(colspan, rowspan)

        self._reg[self._path + "type"] = type
        if var is not None: self._set("var", var)
        if props is not None: self._set("props", props)
        if label is not None: self._set("label", label)
        self._set("index", index)

        if var not in self._ds.var:
            self._ds.var.create(self.type(), var)

        if props is not None and props not in self._ds.var:
            self._ds.var.create("props", props)

    def change_vars(self, map):
        var = self._get("var")
        if var in map:
            self._set("var", map[var])
        props = self._get("props")
        if props in map:
            self._set("props", map[props])

    def _base_id(self):
        return self._get("var")

    def params(self):
        return self._dict()

    def variable_ids(self):
        ids = [self._get("var")]
        props = self._get("props")
        if props is not None:
            ids.append(props)
        return ids

    def __getattr__(self, item):
        if item =="sv":
            return self.single_value()
        raise KeyError(item)

    def single_value(self):
        var = self._get("var")
        return self._ds._single_item_value[var]

    def data(self, group_id, item_id):
        if self._path + "var" not in self._reg:
            return None
        var_id = self._get("var")
        if (group_id, item_id) not in self._ds.var[var_id]:
            return None
        value = self._ds.var[var_id][group_id, item_id]
        file = value.file()

        props_file = None
        if self._path + "props" in self._reg:
            var_id = self._get("props")
            if (group_id, item_id) in self._ds.var[var_id]:
                value = self._ds.var[var_id][group_id, item_id]
                props_file = value.file()

        return self.DataClass(file, props_file, var_id=var_id)