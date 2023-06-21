#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

from .filesystem import File
from copy import deepcopy
from .type import FAIL

MAX_INT = 2**16 - 1

class JsonRegistryNode:
    def __init__(self, reg, path):
        self._reg = reg
        self._path = path

    def _get(self, key, default=None):
        if self._path + key in self._reg:
            return self._reg[self._path + key]
        if default is FAIL:
            raise Exception(f"cannot access JSON registry key {self._path + key}")
        return default

    def _set(self, key, value):
        self._reg[self._path + key] = value

    def _exists(self):
        return self._path in self._reg

    def _remove(self, key):
        if self._path + key in self._reg:
            del self._reg[self._path + key]

    def _keys(self):
        if not self._exists(): return []
        return list(self._reg[self._path].keys())

    def _values(self):
        if not self._exists(): return []
        return list(self._reg[self._path].values())

    def _items(self):
        if not self._exists():
            return []
        return self._reg[self._path].items()

    def _dict(self):
        if not self._exists():
            return {}
        return deepcopy(self._reg[self._path])

class RegistryPath:
    def __init__(self, *args):
        if len(args) == 1:
            arg = args[0]
            if isinstance(arg, str):
                self._path = list(arg.split('/'))
            else:
                self._path = list(arg._path)
        else:
            self._path = list(args)

    def __repr__(self):
        return '/'.join(self._path)

    def copy(self):
        return deepcopy(self)

    def path(self):
        return deepcopy(self._path)

    def append(self, *args):
        copy = self.copy()
        for arg in args:
            if arg == '..': copy._path.pop()
            else: copy._path.append(str(arg))
        return copy

    def __add__(self, other):
        if isinstance(other, RegistryPath):
            return self.append(other._path)
        else:
            return self.append(other)

    def sub_key(self):
        copy = self.copy()
        copy._path.pop(0)
        return copy

    def __getitem__(self, index):
        return self._path[index]

    def __len__(self):
        return len(self._path)

def _getitem(d, key, full_key):
    if len(key) == 0:
        return d

    if len(key) == 1:
        if str(key) not in d:
            raise KeyError(full_key)
        return d[str(key)]

    sub_key = key.sub_key()
    current_key = str(key[0])
    if current_key not in d:
        raise KeyError(full_key)
    return _getitem(d[current_key], sub_key, full_key)

def _contains(d, key):
    if len(key) == 0:
        raise Exception(f"empty key encountered in _contains")

    if len(key) == 1:
        return str(key) in d

    sub_key = key.sub_key()
    current_key = str(key[0])
    if current_key not in d:
        return False
    return _contains(d[current_key], sub_key)

def _setitem(d, key, value, dict_class=dict):
    if len(key) == 0:
        raise Exception(f"empty key encountered in _setitem")

    if len(key) == 1:
        d[str(key)] = value
        return

    sub_key = key.sub_key()
    current_key = str(key[0])
    if current_key not in d:
        d[current_key] = dict_class()
    _setitem(d[current_key], sub_key, value)

def _delitem(d, key):
    if len(key) == 0:
        raise Exception(f"empty key encountered in _delitem")

    if len(key) == 1:
        if str(key) in d:
            del d[str(key)]
        return

    sub_key = key.sub_key()
    current_key = str(key[0])
    if current_key not in d:
        return

    _delitem(d[current_key], sub_key)

    if len(d[current_key]) == 0:
        del d[current_key]

class JsonRegistry(dict):
    def __init__(self, file=None):
        self._file = file
        self._key_cache = {}

    def to_dict(self):
        return dict(deepcopy(self))

    def from_dict(self, data):
        self.clear()
        self.update(data)

    def read(self, file=None):
        if file is None:
            file = self._file
        self.clear()
        self.update(File(file).read())
        self._file = file

    def write(self, file=None):
        if file is None:
            file = self._file
        File(file).write(self.to_dict())
        self._file = file

    def __getitem__(self, key):
        try:
            return self._key_cache[str(key)]
        except:
            pass
        if '/' not in str(key):
            return super().__getitem__(str(key))
        key = RegistryPath(key)
        return _getitem(self, key, key)

    def get(self, key, default):
        if key in self:
            return self[key]
        return default

    def __setitem__(self, key, value):
        self._key_cache[str(key)] = value
        if '/' not in str(key):
            return super().__setitem__(str(key), value)
        key = RegistryPath(key)
        return _setitem(self, key, value)

    def remove(self, key):
        self._key_cache.pop(str(key), None)
        if '/' not in str(key):
            if not str(key) in self:
                return
            return super().__delitem__(str(key))
        key = RegistryPath(key)
        return _delitem(self, key)

    def __delitem__(self, key):
        self.remove(key)

    def __contains__(self, key):
        if '/' not in str(key):
            return super().__contains__(str(key))
        key = RegistryPath(key)
        return _contains(self, key)