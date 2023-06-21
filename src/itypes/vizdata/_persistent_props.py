#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

from ..filesystem import File
from ..properties import Properties


class _PersistentProperties:
    def __init__(self, data=None, file=None):
        if file is None and isinstance(data, File):
            self._file = File(data)
            self._data = None
        else:
            self._data = data
            self._file = File(file) if file is not None else None

        self._valid = self._data is not None or self._file is not None
        self._head = "memory" if self._data is not None else "disk"

    def valid(self):
        return self._valid

    def _to_memory(self):
        if self._head != "memory"  and self._file is not None:
            self._data = Properties(self._file).read()
            self._head = "memory"

    def reload(self):
        self._head = "disk"

    def file(self):
        return self._file

    def data(self):
        self._to_memory()
        return self._data

