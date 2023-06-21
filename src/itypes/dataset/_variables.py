#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

from ..json_registry import RegistryPath
from .variables import _instantiate_variable
from ..utils import align_tabs
from ._node import _DatasetNode
from ..log import log as logger


class _Iterator:
    def __init__(self, variables):
        self._variables = variables
        self._ids = variables.ids()
        self._index = 0

    def __next__(self):
        if self._index >= len(self._ids):
            raise StopIteration

        value = self._variables[self._ids[self._index]]
        self._index += 1
        return value


class _Variables(_DatasetNode):
    def __init__(self, ds):
        super().__init__(ds, RegistryPath("variables"))

    def __contains__(self, id):
        return self._path + id in self._reg

    def __getitem__(self, id):
        path = self._path + id
        if path not in self._reg:
            raise Exception(f"Variable at path \"{path}\" does not exist")
        type = self._reg[self._path + id + "type"]
        return _instantiate_variable(type, self._ds, path)

    def __delitem__(self, id):
        self.remove(id)
        self._ds._do_auto_write()

    def __iter__(self):
        return _Iterator(self)

    def ids(self):
        return self._keys()

    def remove(self, id, delete_files=False):
        if delete_files:
            for value in self[id]:
                value.delete_file()
        self._reg.remove(self._path + id)

    def create(self, type, id):
        path = self._path + id
        if path in self._reg:
            self._reg.remove(self._path + id)
        d = {
            "type": type
        }
        self._reg[self._path + id] = d
        return self[id]

    def __str__(self):
        return self.str()

    def str(self, prefix="", indent="  ", show_res=False):
        return align_tabs(self._str(prefix, indent), show_res)

    def _str(self, prefix="", indent="  ", show_res=False):
        str = ""
        for var in self:
            str += var._str(prefix, indent, show_res)
        return str

    def __setitem__(self, id, var):
        var = self.create(var.type(), var.id())
        var.copy_from(var, indexing="linear", mode="ref")

    def copy_from(self, other, indexing="linear", mode="ref", include_data=True):
        for other_var in other:
            var = self.create(other_var.type(), other_var.id())
            if include_data:
                var.copy_from(other_var, indexing=indexing, mode=mode)

    def verify(self, log=True):
        succeeded = True
        for var in self:
            if log:
                logger.info(f"Checking variable {var.id()}")
            for value in var:
                found = True
                gid, iid = value.group_id(), value.item_id()
                if gid not in self._ds.seq:
                    found = False
                elif iid not in self._ds.seq[gid]:
                    found = False
                if not found and log:
                    logger.warning(f"Value for variable discovered {var.id()} for non-existent item {iid}/{gid}")

                if not value.is_scalar():
                    if not value.file().exists():
                        if log:
                            logger.error(f"File {value.file()} for item {iid}/{gid} variable {var.id()} does not exist")
                        succeeded = False

            for item in self._ds:
                gid, iid = item.group_id(), item.id()
                if ((gid, iid) not in var) and log:
                    logger.warning(f"Item {iid}/{gid} missing value for variale {var.id()}")

        return succeeded

    def sanitize(self, log=True):
        for var in self:
            if log:
                logger.info(f"Checking variable {var.id()}")

            used = False
            for viz in self._ds.viz:
                if var.id() in viz.variable_ids(): used = True
            for met in self._ds.met:
                if var.id() in met.variable_ids(): used = True

            if not used:
                if log:
                    logger.warning(f"Removing unused variable {var.id()}")
                del self[var.id()]
                continue

            remove_keys = []
            for value in var:
                found = True
                gid, iid = value.group_id(), value.item_id()
                if gid not in self._ds.seq:
                    found = False
                elif iid not in self._ds.seq[gid]:
                    found = False

                if not found:
                    if log:
                        logger.warning(f"Removing value for variable {var.id()} for non-existent item {iid}/{gid}")
                    remove_keys.append((gid, iid))

                if not value.is_scalar():
                    if not value.file().exists():
                        if log:
                            logger.warning(f"File {value.file()} for item {iid}/{gid} variable {var.id()} does not exist")

            for key in remove_keys:
                del var[key]

            for item in self._ds:
                gid, iid = item.group_id(), item.id()
                if ((gid, iid) not in var) and log:
                    logger.warning(f"Item {iid}/{gid} missing value for variale {var.id()}")

        return True