#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

from ..json_registry import RegistryPath
from .visualizations.registry import _instantiate_visualization, _reinstantiate_visualization
from ..type import is_list
from ..utils import align_tabs
from ..grid2d import Grid2D
from ._node import _DatasetNode
from ..log import log as logger
from itypes import Struct 


class _Iterator:
    def __init__(self, viz):
        self._viz = viz
        self._indices = viz.indices()
        self._index = 0

    def __next__(self):
        if self._index >= len(self._indices):
            raise StopIteration

        value = self._viz[self._indices[self._index]]
        self._index += 1
        return value
    

class _Visualizations(_DatasetNode):
    class _Row:
        def __init__(self, visualizations, row_idx):
            self._visualizations = visualizations
            self._row_idx = row_idx
            self._current_col = 0

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, tb):
            if exc_type is None:
                return self

        def skip_cell(self):
            idx = self._current_col, self._row_idx
            if idx in self._visualizations:
                self._visualizations.remove(idx)
            self._current_col += 1
            return self

        def add_cell(self, type, **kwargs):
            index = self._current_col, self._row_idx
            kwargs['index'] = index
            viz = _instantiate_visualization(
                self._visualizations._ds,
                self._visualizations._path,
                type,
                **kwargs
            )
            self._current_col += 1
            while self._visualizations.is_occupied((self._current_col, self._row_idx)):
                self._current_col += 1
            return viz

    class _Column:
        def __init__(self, visualizations, col_idx):
            self._visualizations = visualizations
            self._col_idx = col_idx
            self._current_row = 0

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, tb):
            if exc_type is None:
                return self

        def skip_cell(self):
            idx = self._col_idx, self._current_row
            if idx in self._visualizations:
                self._visualizations.remove(idx)
            self._current_row += 1
            return self

        def add_cell(self, type, **kwargs):
            index = self._col_idx, self._current_row
            kwargs['index'] = index
            viz = _instantiate_visualization(
                self._visualizations._ds,
                self._visualizations._path,
                type,
                **kwargs
            )
            self._current_row += 1
            while self._visualizations.is_occupied((self._col_idx, self._current_row)):
                self._current_row += 1
            return viz

    def __init__(self, ds):
        super().__init__(ds, RegistryPath("visualizations"))
        self._current_col = 0
        self._current_row = 0

    def is_occupied(self, index):
        col, row = index
        for viz in self:
            viz_col, viz_row = viz.index()
            viz_cs, viz_rs = viz.colspan(), viz.rowspan()
            if col >= viz_col and col < viz_col + viz_cs and \
               row >= viz_row and row < viz_row + viz_rs:
                return True
        return False

    def new_row(self):
        row = self._Row(self, self._current_row)
        self._current_row += 1
        return row

    def new_col(self):
        col = self._Column(self, self._current_col)
        self._current_col += 1
        return col

    def create(self, type, index, **kwargs):
        kwargs['index'] = index
        viz = _instantiate_visualization(
            self._ds,
            self._path,
            type,
            **kwargs
        )
        self._ds._do_auto_write()
        return viz

    def merge_in(self, other, mode=None, **kwargs):
        params = other.params()
        params.update(kwargs)
        viz = _instantiate_visualization(
            self._ds,
            self._path,
            **params
        )
        if mode is not None:
            for new_id, old_id in zip(viz.variable_ids(), other.variable_ids()):
                new_var = self._ds.var[new_id]
                old_var = self._ds.var[old_id]
                self._ds.var.create(type=old_var.id(), id=new_id)
                new_var.copy_from(old_var, mode=mode)

    def indices(self):
        indices = []
        for value in list(self._values()):
            indices.append(value['index'])
        return indices

    def _new_id(self, base_id):
        path = self._path
        if path not in self._reg:
            return base_id
        idx = 1
        id = base_id
        id_path = path + base_id
        while id_path in self._reg:
            id = "%s-%d" % (base_id, idx)
            id_path = path + id
            idx += 1
        return id

    def ids(self):
        return self._keys()

    def __contains__(self, id):
        if is_list(id):
            return id in self.indices()
        else:
            return self._path + id in self._reg

    def __getitem__(self, id):
        if is_list(id):
            if not self._exists():
                raise Exception(f"visualization \"{id}\" not found")
            for key, value in self._reg[self._path].items():
                if value['index'] == id:
                    return _reinstantiate_visualization(
                        self._ds,
                        self._path + key,
                     )
            raise Exception(f"visualization \"{id}\" not found")
        else:
            return _reinstantiate_visualization(
                self._ds,
                self._path + id,
            )

    def __delitem__(self, id):
        self.remove(id)
        self._ds._do_auto_write()

    def __iter__(self):
        return _Iterator(self)

    def remove(self, id):
        if is_list(id):
            for key, value in self._items():
                if value['index'] == id:
                    self._reg.remove(self._path + key)
            raise Exception(f"visualization \"{id} not found")
        else:
            self._reg.remove(self._path + id)

    def __str__(self):
        return self.str()

    def str(self, prefix="", indent="  "):
        return align_tabs(self._str(prefix, indent))

    def _str(self, prefix="", indent="  "):
        str = ""
        for viz in self:
            str += viz._str(prefix, indent) + "\n"
        return str

    def __setitem__(self, id, viz):
        params = viz.params()
        self.create(**params, id=id)

    def copy_from(self, other):
        for other_viz in other:
            self.create(**other_viz.params(), id=other_viz.id())

    def verify(self, log=True):
        succeeded = True
        for viz in self:
            if log:
                logger.info(f"Checking visualization {viz.id()}")
            for var_id in viz.variable_ids():
                if var_id not in self._ds.var:
                    succeeded = False
                    if log:
                        logger.error(f"Visualization {viz.id()} references non-existent variable {var_id}")

        return succeeded

    def sanitize(self, log=True):
        remove_list = []
        for viz in self:
            if log:
                logger.info(f"Checking visualization {viz.id()}")
            for var_id in viz.variable_ids():
                if var_id not in self._ds.var:
                    remove_list.append(viz.id())
                    if log:
                        logger.warning(f"Removing visualization {viz.id()} as it references non-existent variable {var_id}")

        for id in remove_list:
            del self[id]

        return True
    
    def dimensions(self):
        s = Struct() 
        if len(self.ids()) == 0:
            s.min_row = 0
            s.max_row = 0
            s.min_col = 0
            s.max_col = 0
            s.cols = 0
            s.row = 0
            return s 

        s.min_row = 10000
        s.max_row = -10000
        s.min_col = 10000
        s.max_col = -10000

        for viz in self: 
            col, row = viz.index() 
            if col < s.min_col: s.min_col = col 
            if col > s.max_col: s.max_col = col
            if row < s.min_row: s.min_row = row
            if row > s.max_row: s.max_row = row

        s.cols = s.max_col - s.min_col + 1
        s.rows = s.max_row - s.min_row + 1

        return s