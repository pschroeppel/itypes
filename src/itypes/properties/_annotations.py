#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

from ..json_registry import RegistryPath
from .annotations import _instantiate_annotation, _reinstantiate_annotation
from ..json_registry import JsonRegistryNode


class _Iterator:
    def __init__(self, annotations):
        self._annotations = annotations
        self._ids = annotations.ids()
        self._index = 0

    def __next__(self):
        if self._index >= len(self._ids):
            raise StopIteration

        value = self._annotations[self._ids[self._index]]
        self._index += 1
        return value


class _Annotations(JsonRegistryNode):
    def __init__(self, props):
        super().__init__(props._reg, RegistryPath("annotations"))
        self._props = props
        self._new_item_counter = 0

    def __contains__(self, id):
        return self._path.append(id) in self._reg

    def __getitem__(self, id):
        path = self._path + id
        if path not in self._reg:
            raise Exception(f"Annotation at path \"{path}\" does not exist")
        return _reinstantiate_annotation(self._props, path)

    def __delitem__(self, id):
        self.remove(id)
        self._props._do_auto_write()

    def __iter__(self):
        return _Iterator(self)

    def ids(self):
        path = self._path
        if path not in self._reg:
            return []
        return list(self._reg[path].keys())

    def remove(self, id):
        self._reg.remove(self._path + id)

    def _new_id(self):
        id = "%08d" % self._new_item_counter
        self._new_item_counter += 1
        return id

    def create(self, type, **kwargs):
        id = kwargs.pop("id", None)
        if id is None:
            id = self._new_id()

        path = self._path + id
        return _instantiate_annotation(type, self, path, **kwargs)


