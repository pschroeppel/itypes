#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

import os
import re
import shutil
from copy import deepcopy
from .helper import split_path, mkdirs


rx_id = re.compile(r'\d+')


def abspath(path):
    if '//' in path:
        index = path.index('//')
        path = path[index + 1:]
    return os.path.abspath(path)


class Path:
    def __init__(self, path=None, absolute=False):
        if path is None:
            path = ''
        if isinstance(path, Path):
            path = path.str()
        if absolute:
            path = abspath(str(path))

        self._parts = split_path(path)

    def clone(self):
        return deepcopy(self)

    def name(self):
        return self._parts[-1]

    def mkdir(self):
        mkdirs(self.str())
        return self

    def exists(self):
        from .io import exists
        return exists(self.abs().str())

    def is_dir(self):
        from .io import is_dir
        return is_dir(self.abs().str())

    def empty(self):
        return len(os.listdir(self.str())) == 0

    def remove(self):
        if self.exists():
            shutil.rmtree(str(self.abs()))

    def cd(self, *parts):
        n = self.clone()
        for part in parts:
            if isinstance(part, Path):
                n._parts += part._parts
            else:
                more_parts = split_path(part)
                n._parts += more_parts
        return n

    def search_files(self, *patterns):
        result = []
        for file in self.list_files():
            for pattern in patterns:
                if file.matches(pattern):
                    result.append(file)
        for dir in self.list_dirs():
            result += dir.search_files(*patterns)
        return result

    def list_dirs(self, pattern=None):
        if not self.exists():
            raise FileNotFoundError(self.str())

        dir = self.str()
        if dir == '': dir = '.'
        list_dirs = sorted([f.path for f in os.scandir(dir) if f.is_dir()])
        list = [Path(p) for p in list_dirs]
        if pattern is not None:
            rx = re.compile(pattern)
            new_list = []
            for entry in list:
                if rx.match(entry.name()):
                    new_list.append(entry)
            list = new_list
        return list

    def list_files(self, pattern=None):
        from .file import File

        if not self.exists():
            raise FileNotFoundError(self.str())

        dir = self.str()
        if dir == '': dir = '.'
        list_files = sorted([f.path for f in os.scandir(dir) if f.is_file()])
        list = [File(p) for p in list_files]
        if pattern is not None:
            rx = re.compile(pattern)
            new_list = []
            for entry in list:
                if rx.match(entry.name()):
                    new_list.append(entry)
            list = new_list
        return list

    def is_relative(self):
        return self._parts[0] == ".."

    def rel_to(self, other):
        if not isinstance(other, Path):
            other = Path(other)

        abs_self = self.abs().str()
        abs_other = other.abs().str()

        return Path(os.path.relpath(abs_self, abs_other))

    def __add__(self, other):
        from .file import File

        filename = None
        if isinstance(other, File):
            filename = other.name()
            other = other.path()

        if not isinstance(other, Path):
            other = Path(other)

        combined = Path(os.path.normpath(os.path.join(self.str(), other.str())))
        if filename is not None:
            return combined.file(filename)
        else:
            return combined

    def file(self, filename):
        from .file import File
        """ new_file():
        E.g. Path('/a/b/f.e').new_file('y.z') returns '/a/b/y.z'
        """
        return File(path=self, name=filename)

    def part(self, idx):
        """ sub(idx):
        E.g. Path('/a/b').sub(-1) returns 'b'
        """
        return self._parts[idx]

    def parts(self):
        return self._parts

    def abs(self):
        return Path(abspath(self.str()))

    def str(self):
        return '/'.join(self._parts)

    def str_index(self):
        """ str_id():
        E.g. Path('/a/b/f0000.e').str_id() returns '0000'
        """
        m = rx_id.search(self.name())
        if not m: return None
        return m.group(0)

    def index(self):
        """ str_id():
        E.g. Path('/a/b/f0000.e').str_id() returns 0
        """
        x = self.str_index()
        if x is None: return -1
        return int(x)

    def __eq__(self, other):
        return self.str() == other.str()

    def __str__(self):
        return self.str()


home = Path(os.path.join(os.getenv("HOME")))
