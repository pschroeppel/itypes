#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

from ..attr_dict import AttrDict
from .helper import _translate, _apply, _flatten, _flatten_keys, _dict_to_str, _create_empty, KeyPath
from copy import deepcopy
from ..type import is_list


class Struct(AttrDict):
    def clone_type(self, *args, **kwargs):
        return Struct(*args, **kwargs)

    def clone(self, clone_functions=None):
        if clone_functions is None:
            clone_functions = []
        clone_functions.append((lambda x: True, lambda x: deepcopy(x)))
        return _translate(self, clone_functions)

    def translate(self, func, *args, **kwargs):
        return _translate(self, func, *args, **kwargs)

    def apply(self, func, *args, **kwargs):
        _apply(self, func, *args, **kwargs)

    def flatten(self):
        result = type(self)()
        _flatten(self, None, result)
        return result

    def flat_keys(self):
        return _flatten_keys(self, None, None)

    def copy(self):
        return deepcopy(self)

    def create_empty(self, template=None):
        return _create_empty(self, template)

    def merge_with(self, other):
        new = other.create_empty(template=self)

        for key in other.flat_keys():
            new[key] = other[key]

        return new

    def str(self, indent=1, prefix=''):
        pairs = _dict_to_str(self, indent)
        max_key_len = 0
        for key, value in pairs:
            max_key_len = max(len(prefix + key), max_key_len)
        result = ''
        for key, value in pairs:
            result += "{0:{1}} {2}\n".format(prefix + key + ':', max_key_len + 4, value)
        return result

    def __getitem__(self, item):
        if item == "__deepcopy__":
            raise AttributeError(item)

        if isinstance(item, KeyPath):
            return item.get(self)
        else:
            return super().__getitem__(item)

    def __setitem__(self, key, value):
        if isinstance(key, KeyPath):
            key.set(self, value)
        else:
            super().__setitem__(key, value)
        return

    def __contains__(self, item):
        try:
            self.__getitem__(item)
            return True
        except:
            return False

    def __str__(self):
        return self.str()


