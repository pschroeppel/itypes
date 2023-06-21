#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

from itypes import Path
from ..filesystem import File
from ._node import _DatasetNode


class _Value(_DatasetNode):
    def variable_id(self):
        path = self._path + ".." + ".." + ".."
        return str(path[-1])

    def variable(self):
        return self._ds.var[self.variable_id()]

    def type(self):
        path = self._path + ".." + ".." + ".." + "type"
        return self._reg[path]

    def group_id(self):
        return str(self._path[-2])

    def item_id(self):
        return str(self._path[-1])

    def copy_from(self, other, mode="ref"):
        if mode == "ref": self.set_ref(other.file())
        else:             self.set_data(other.data())

    def set_ref(self, file, rel_to="cwd", check_if_exists=False):
        if file is None:
            self._reg.remove(self._path + "path")
            return

        file = File(file)

        if rel_to == "cwd":
            file = file.abs()
        elif rel_to == "output":
            base_path = self._ds.base_path()
            file = base_path.cd(file.path()).file(file.name()).abs()
        else:
            raise Exception("rel_to must be 'cwd' or 'output'")

        if check_if_exists:
            if not file.exists():
                raise Exception(f"External sequence file '{file}' does not exist")

        if not self._ds._abs_paths:
            file = file.rel_to(self._ds.base_path())

        self._reg[self._path + "path"] = str(file)

        self._ds._do_auto_write()

    def set_data(self, data, extension=None, **kwargs):
        if data is None:
            self._reg.remove(self._path + "path")
            return

        variable = self.variable()
        item = self._ds.seq[self.group_id()][self.item_id()]

        if variable.is_scalar():
            self._reg[self._path + "value"] = data
        else:
            if extension is None:
                extension = variable.extension()

            if self._ds._structured:
                file = Path(self.group_id()).cd(self.item_id()).file(f"{self.variable_id()}.{extension}")
            else:
                linear_format = self._ds._linear_format
                linear_index = item.linear_index()
                if "{var}" not in linear_format:
                    raise Exception("linear_format needs to contain '{var}'")
                if '%' in linear_format: indexed = linear_format % linear_index
                else:                    indexed = linear_format
                filename = indexed.replace("{var}", self.variable_id()) + '.' + extension
                file = File(filename)

            abs_file = (self._ds.base_path() + file.path()).abs().file(file.name())
            variable.write(abs_file, data, **kwargs)
            self._reg[self._path + "path"] = str(file) if not self._ds._abs_paths else str(abs_file)

        self._ds._do_auto_write()

        return self

    def is_scalar(self):
        return self.variable().is_scalar()

    def file(self):
        if self._path + "path" not in self._reg:
            return None
        file = File(self._reg[self._path + "path"])
        path = self._ds.base_path()
        if path is not None:
            path = path.cd(file.path()).abs()
            return path.file(file.name())
        return file

    def delete_file(self):
        if self.is_scalar():
            return
        file = self.file()
        if file is None:
            return
        file.remove()

    def data(self, **kwargs):
        variable = self.variable()
        if variable.is_scalar():
            if self._path + "value" in self._reg:
                return self._reg[self._path + "value"]
            return None
        else:
            file = self.file()
            if file is None:
                return None
            file = File(file)
            return self.variable().read(file, **kwargs)
