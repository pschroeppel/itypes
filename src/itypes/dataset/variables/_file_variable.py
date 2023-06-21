#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

from ...filesystem import File
from ._variable import _Variable


class _FileVariable(_Variable):
    def extension(self):
        raise NotImplementedError

    def read(self, file, **kwargs):
        if file is None:
            return None
        file = File(file)
        return file.read(**kwargs)

    def write(self, file, data, **kwargs):
        if file is None:
            raise Exception(f"write() needs a file")
        if data is None:
            return
        if file.extension() == "json" and hasattr(data, "to_dict"):
            data = data.to_dict()
        file = File(file)
        file.write(data, **kwargs)
        return self

    def is_scalar(self):
        return False