#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

from copy import copy
from ...utils import align_tabs
from .._node import _DatasetNode


class _Visualization(_DatasetNode):
    def __init__(self, ds, base_path=None, path=None):
        super().__init__(ds, path)

        self._base_path = base_path
        self._id = path[-1] if path is not None else None

    def id(self):
        return self._id

    def type(self):
        return self._get("type")

    def create(self, colspan=None, rowspan=None):
        if colspan is not None: self._set("colspan", colspan)
        if rowspan is not None: self._set("rowspan", rowspan)

    def rowspan(self):
        rowspan = self._get("rowspan")
        if rowspan is None: return 1
        return rowspan 

    def colspan(self):
        colspan = self._get("colspan")
        if colspan is None: return 1
        return colspan 

    def index(self):
        return self._get("index")

    def _base_id(self):
        raise NotImplementedError

    def _str(self, prefix="", indent="  "):
        return prefix + f"{self.id()+':'}\ttype={self.type()}\tindex={tuple(self.index())}\tvars=[{','.join(self.variable_ids())}]"

    def str(self, prefix="", indent="  "):
        return align_tabs(self._str(prefix, indent))

    def __str__(self):
        return self.str()