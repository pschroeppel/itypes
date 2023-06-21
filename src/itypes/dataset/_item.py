#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

from ..utils import align_tabs
from ._node import _DatasetNode


class _Iterator:
    def __init__(self, item):
        self._item = item
        self._ids = item.variable_ids()
        self._index = 0

    def __next__(self):
        if self._index >= len(self._ids):
            raise StopIteration

        value = self._item[self._ids[self._index]]
        self._index += 1
        return value


class _Item(_DatasetNode):
    def __init__(self, ds, path, label=None, index=None):
        super().__init__(ds, path)

        self._item_id = self._path[-1]
        self._group_id = self._path[-3]
        self._group_label = self._reg[self._path + ".." + ".." + "label"]

        exists = self._path in self._reg
        if not exists:
            self._ds.seq._append_item(self._group_id, self._item_id, self._group_label, label)

        if label is not None:
            self._set("label", label)

        if index is not None:
            self._set("index", index)

    def __iter__(self):
        return _Iterator(self)

    def linear_index(self):
        return self._get("index")

    def set_linear_index(self, index):
        self._set("index", index)

    def id(self):
        return self._item_id

    def group_id(self):
        return self._group_id

    def group_label(self):
        return self._group_label

    def label(self):
        return self._get("label")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is None:
            return self

    def remove(self, delete_files=False):
        gid, iid = self.group_id(), self.id()
        self._ds.seq.remove_item((gid, iid))
        for var in self._ds.var:
            if (gid, iid) in var:
                var.remove_item((gid, iid), delete_files=delete_files)

    def variable_ids(self):
        ids = []
        for variable in self._ds.var:
            if variable.id() in self:
                ids.append(variable.id())
        return ids

    def __getitem__(self, variable_id):
        if variable_id not in self._ds.var:
            raise Exception(f"\"{variable_id}\" is not an existing variable")
        return self._ds.var[variable_id][self._group_id, self._item_id]

    def __contains__(self, variable_id):
        if variable_id not in self._ds.var:
            return False
        return (self._group_id, self._item_id) in self._ds.var[variable_id]


    def __str__(self):
        return self.str()

    def str(self):
        return align_tabs(self._str())

    def _str(self):
        str = ""
        str += f"{self.id()}"
        if self.label() is not None:
            str += f"\tlabel=\"{self.label()}\""
        return str

    def set_struct(self, struct):
        for variable in struct.keys():
            if variable not in self._ds.var:
                continue
            self[variable].set_data(struct[variable], dims=struct.dims)

        self._ds._do_auto_write()

        return self

    def numpy_struct(self, dims):
        import numpy as np
        from ..struct import NumpyStruct
        struct = NumpyStruct(dims)
        for variable_id in self:
            struct[variable_id] = self[variable_id].data(dims=dims, dtype=np.float32)
        struct.item_id = self.id()
        struct.group_id = self.group_id()
        return struct

    def torch_struct(self, dims, device):
        import numpy as np
        from ..struct import TorchStruct
        struct = TorchStruct(dims)
        for value in self:
            struct[value.variable_id()] = self[value.variable_id()].data(dims=dims, dtype=np.float32, device=device)
        struct.item_id = self.id()
        struct.group_id = self.group_id()
        return struct