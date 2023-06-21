#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

from collections import OrderedDict
from .type import is_dict

class AttrDict(OrderedDict):
    def clone_type(self, *args, **kwargs):
        return AttrDict(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super().__init__()

        if len(args) and is_dict(args[0]):
            for key, value in args[0].items():
                if is_dict(value):
                    value = self.clone_type(value)
                self[key] = value

        d = dict(**kwargs)
        for key, value in d.items():
            if is_dict(value):
                value = self.clone_type(value)
            self[key] = value

    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, key):
        return self[key]

    def __getstate__(self):
        return self

    def __setstate__(self, state):
        for key, value in state.items():
            self[key] = value

            