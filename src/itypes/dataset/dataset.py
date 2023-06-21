#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

import os
from ._sequence import _Sequence
from ._variables import _Variables
from ._metrics import _Metrics
from ._visualizations import _Visualizations
from ..json_registry import JsonRegistry, RegistryPath
from ..filesystem import File, Path
from ..utils import align_tabs


class _Iterator:
    def __init__(self, ds):
        self._ds = ds
        self._indices = self._ds.seq.full_item_list()
        self._index = 0

    def __next__(self):
        if self._index >= len(self._indices):
            raise StopIteration

        item = self._indices[self._index]
        item_id = item["item_id"]
        group_id = item["group_id"]
        value = self._ds.seq[group_id][item_id]
        self._index += 1
        return value


class Dataset:
    def __init__(self,
                 file=None,
                 abs_paths=False,
                 auto_write=False,
                 structured=True,
                 single_item=False,
                 linear_format="%08d-{var}"):

        self._reg = JsonRegistry(file)
        self._abs_paths = abs_paths
        self._auto_write = auto_write
        self._structured = structured
        self._linear_format = linear_format
        self._single_item = single_item
        self.viz = _Visualizations(self)
        self.var = _Variables(self)
        self.seq = _Sequence(self)
        self.met = _Metrics(self)
        self._file = self._make_file(file) if file is not None else None

        self._single_item = single_item
        if single_item:
            self._structured = False
            self._linear_format = "{var}"
            self._single_item_value = self.seq.group().item()

        self._merge_index = [0, 0]

    def _do_auto_write(self):
        if self._auto_write:
            self.write()

    def file(self):
        return self._file

    def base_path(self):
        if self._file is None:
            return None
        return self._file.path()

    def to_dict(self):
        return self._reg.to_dict()

    def _make_file(self, file):
        if Path(str(file)).is_dir():
            config_file = Path(str(file)).file('data.gridseq')
            if config_file.exists():
                return config_file
            config_file = Path(str(file)).file('data.json')
            return config_file
        org_file = file
        file = File(file)
        if file.extension() not in ["json", "gridseq"]:
            file = Path(str(org_file)).file("data.json")
        return file

    def write(self, file=None):
        if file is None:
            file = self._file
        file = self._make_file(file)
        self._reg.write(file)
        self._file = file
        return self

    def read(self, file=None):
        if file is None:
            file = self._file
        file = self._make_file(file)

        if not file.exists():
            raise Exception(f"Dataset not found: \"{file}\"")

        if file.extension() == "gridseq":
            from ._legacy import read_gridseq
            read_gridseq(self, file)
            return self

        self._reg.read(file)
        self._file = file
        return self

    def __len__(self):
        return len(self.seq.full_item_list())

    def __delitem__(self, index):
        item = self.seq.full_item_list()[index]
        item_id = item["item_id"]
        group_id = item["group_id"]
        del self.seq[group_id][item_id]
        self._do_auto_write()

    def __getitem__(self, index):
        item = self.seq.full_item_list()[index]
        item_id = item["item_id"]
        group_id = item["group_id"]
        return self.seq[group_id][item_id]

    def __iter__(self):
        return _Iterator(self)

    def __str__(self):
        return self.str()

    def str(self, prefix="", indent="  ", show_res=False):
        return align_tabs(self._str(prefix, indent, show_res))

    def _str(self, prefix="", indent="  ", show_res=False):
        str = ""
        str += prefix + "variables:\n"
        if len(self.var.ids()) == 0:
            str += prefix + "  (none)\n"
        else:
            str += self.var._str(prefix=prefix + indent, indent=indent, show_res=show_res)
        str += prefix + "visualizations:\n"
        if len(self.viz.ids()) == 0:
            str += prefix + "  (none)\n"
        else:
            str += self.viz._str(prefix=prefix + indent, indent=indent)
        str += prefix + "metrics:\n"
        if len(self.met.ids()) == 0:
            str += prefix + "  (none)\n"
        else:
            str += self.met._str(prefix=prefix + indent, indent=indent)
        str += prefix + "sequence:\n"
        if len(self) == 0:
            str += prefix + "  (none)\n"
        else:
            str += self.seq._str(prefix=prefix + indent, indent=indent)
        return str

    def merge(self, other, mode="ref", include_label=False):
        other_dims = other.viz.dimensions()
        col, row = self._merge_index

        if len(self) == 0:
            self.seq.copy_from(other.seq)

        if include_label:
            self.viz.create(
                type="text",
                text="<h2>" + str(other.file())+":" + "</h2>",
                index=(col, row),
                colspan=other_dims.cols
            )
            row += 1

        # Copy variables
        var_mapping = {}
        for var in other.var:
            new_id = var.id()
            idx = 0
            while new_id in self.var:
                idx += 1
                new_id = f"%d_{var.id()}" % idx

            var_mapping[var.id()] = new_id
            self.var.create(type=var.type(), id=new_id)
            self.var[new_id].copy_from(var, mode=mode)

        # Copy visualizaitons
        for viz in other.viz:
            new_id = viz.id()
            idx = 0
            while new_id in self.viz:
                idx += 1
                new_id = f"%d_{viz.id()}" % idx

            params = viz.params()
            params["index"][1] += row
            params["index"][0] += col
            self.viz.create(**params, id=new_id)
            self.viz[new_id].change_vars(var_mapping)

        # Copy metrics
        for met in other.met:
            self.met[met.id()].change_vars(var_mapping)

        self._merge_index[0] += other_dims.cols

    def new_merge_row(self):
        dims = self.viz.dimensions()
        self._merge_index = [0, dims.max_row + 1]

    def copy_from(self, other, mode="ref"):
        self.viz.copy_from(other.viz)
        self.seq.copy_from(other.seq)
        self.var.copy_from(other.var, mode=mode)
        self.met.copy_from(other.met)

    def template_from(self, other, include_metrics=True):
        self.viz.copy_from(other.viz)
        if include_metrics:
            self.met.copy_from(other.met)
        self.var.copy_from(other.var, include_data=False)

    def verify(self, log=True):
        succeeded = True
        succeeded = self.viz.verify(log=log) and succeeded
        succeeded = self.seq.verify(log=log) and succeeded
        succeeded = self.var.verify(log=log) and succeeded
        succeeded = self.met.verify(log=log) and succeeded
        return succeeded

    def sanitize(self, log=True):
        if not self.viz.sanitize(log=log):
            return False
        if not self.met.sanitize(log=log):
            return False
        if not self.var.sanitize(log=log):
            return False
        if not self.seq.sanitize(log=log):
            return False
        return True

    def concat(self, other, mode="ref"):
        for other_group in other.seq:
            group = self.seq.group(self.seq.new_group_id(other_group.id()), other_group.label())
            for other_item in other_group:
                item = group.item(group.new_item_id(other_item.id()), other_item.label())
                for other_value in other_item:
                    var_id = other_value.variable_id()
                    if var_id not in self.var:
                        continue
                    item[var_id].copy_from(other_value, mode=mode)

