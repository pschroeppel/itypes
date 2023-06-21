#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

from ..type import is_str, is_torch, is_numpy
from ..filesystem import File


class _Persistent:
    def __init__(self, data=None, file=None, load_class=None, **read_kwargs):
        if file is None and isinstance(data, File):
            self._file = File(data)
            self._data = None
        else:
            self._data = data
            self._file = File(file) if file is not None else None

        self._load_class = load_class
        self._read_kwargs = read_kwargs
        self._valid = self._data is not None or self._file is not None
        self._head = "memory" if self._data is not None else "disk"

    def valid(self):
        return self._valid

    def _to_memory(self):
        if self._head != "memory"  and self._file is not None:
            self._data = self._file.read(**self._read_kwargs)
            self._head = "memory"

    def reload(self):
        self._head = "disk"

    def file(self):
        return self._file

    def data(self):
        self._to_memory()
        data = self._data
        if self._load_class is not None:
            return self._load_class(data)
        return data

    def numpy(self):
        if not self._valid:
            return None

        self._to_memory()
        if is_numpy(self._data):
            return self._data

        if is_torch(self._data):
            return self._data.detach().cpu().numpy()

        raise Exception(f"Don't know hot to convert {type(self._data)} to numpy")

    def tensor(self, device=None):
        if not self._valid:
            return None

        self._to_memory()
        if is_numpy(self._data):
            import torch
            tensor = torch.from_numpy(self._data)
            if device is not None:
                tensor = tensor.to(device)
            return tensor

        raise Exception(f"Don't know hot to convert {type(self._data)} to tensor")

