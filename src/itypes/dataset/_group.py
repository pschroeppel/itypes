#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

from ._item import _Item
from ..utils import align_tabs
from ._node import _DatasetNode


class _Iterator:
    def __init__(self, group):
        self._group = group
        self._items = group.item_ids()
        self._index = 0

    def __next__(self):
        if self._index >= len(self._items):
            raise StopIteration

        value = self._group[self._items[self._index]]
        self._index += 1
        return value


class _Group(_DatasetNode):
    def __init__(self, ds, path, label=None):
        super().__init__(ds, path)

        exists = self._path in self._reg
        if not exists:
            group_id = self._path[-1]
            self._ds.seq._append_group(group_id, label)

        if label is not None:
            self._reg[self._path + "label"] = label

        self._new_item_counter = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is None:
            return self

    def id(self):
        return self._path[-1]

    def label(self):
        return self._get("label")

    def item_ids(self):
        path = self._path + "items"
        if path not in self._reg:
            return []
        return list(self._reg[path].keys())

    def _new_id(self):
        id = "%08d" % self._new_item_counter
        self._new_item_counter += 1
        return id

    def item(self, id=None, label=None):
        if id is None:
            id = self._new_id()
        if label is None:
            label = id
        path = self._path + "items" + id
        return _Item(self._ds, path, label, self._ds.seq.new_linear_index())

    def remove(self, id, delete_files=False):
        if delete_files:
            raise NotImplementedError

        path = self._path + "items" + id
        del self._reg[path]

        if len(self.item_ids()) == 0:
            del self._reg[self._path]

        self._ds.seq.flag_linear_index_as_dirty()

    def new_item_id(self, name):
        new_name = name
        index = 0
        while new_name in self:
            index += 1
            new_name = f"{index}_{name}"
        return new_name

    def __delitem__(self, id):
        self.remove(id)
        self._ds._do_auto_write()

    def __getitem__(self, id):
        path = self._path + "items" + id
        if path not in self._reg:
            raise KeyError(path)
        return _Item(self._ds, path)

    def __contains__(self, item):
        path = self._path + "items" + item
        return  path in self._reg

    def __iter__(self):
        return _Iterator(self)

    def __str__(self):
        return self.str()

    def str(self, prefix="", indent="  ", start_index=None):
        return align_tabs(self._str(prefix, indent, start_index))

    def _str(self, prefix="", indent="  ", start_index=None):
        str = ""
        str += prefix + f"{self.id()}:"
        if self.label() is not None:
            str += f"\tlabel=\"{self.label()}\""
        str += "\n"
        prefix = prefix + indent
        index = start_index
        for item in self:
            item_prefix = prefix + f"[{index}] "
            str += item_prefix + item._str() + "\n"
            if index is not None: index = index + 1

        return str