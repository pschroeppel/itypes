#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

from ._annotations import _Annotations
from ..filesystem import File
from ..json_registry import JsonRegistry


class Properties:
    def __init__(self,
                 file=None,
                 auto_write=False
    ):
        self._reg = JsonRegistry(file)
        self._auto_write = auto_write
        self.ann = _Annotations(self)
        self._file = File(file) if file is not None else None

    def _do_auto_write(self):
        if self._auto_write:
            self.write()

    def to_dict(self):
        return self._reg.to_dict()

    def write(self, file=None):
        if file is None:
            file = self._file
        file = File(file)
        self._reg.write(file)
        self._file = file
        return self

    def read(self, file=None):
        if file is None:
            file = self._file
        file = File(file)

        self._reg.read(file)
        self._file = file
        return self
