#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

from ..json_registry import JsonRegistryNode


class _DatasetNode(JsonRegistryNode):
    def __init__(self, ds, path):
        super().__init__(ds._reg, path)
        self._ds = ds

    def _get_var(self, key, type=None, create=False):
        var_id = self._get(key)
        if var_id is None:
            return None
        if var_id not in self._ds.var:
            if create:
                return self._ds.var.create(type=type, id=var_id)
            else:
                return None
        return self._ds.var[var_id]