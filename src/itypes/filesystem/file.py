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
from .io import read, write
from .helper import split_path
from ..wildcard import wildcard_match


rx_id = re.compile(r'\d+')


class File:
    def __init__(self, name, path=None):
        from .path import Path

        if isinstance(name, File):
            name = name.str()

        if '/' in name:
            parts = split_path(name)
            name = parts[-1]
            if path is None:
                path = Path('/'.join(parts[:-1]))
            else:
                subdir = '/'.join(parts[:-1])
                path = path.cd(subdir)

        if path is None:
            path = Path()

        self._name = name
        self._path = path

    def open(self, mode):
        self._path.mkdir()
        from .io import _open
        return _open(self.str(), mode)

    def str(self):
        return os.path.join(self._path.str(), self._name)

    def abs(self):
        return File(self._name, self._path.abs())

    def rel_to(self, other):
        if isinstance(other, str):
            from .path import Path
            other = Path(other)
        return File(self._name, self._path.rel_to(other))

    def name(self):
        return self.basename(False)

    def matches(self, pattern):
        if wildcard_match([self.name()], pattern):
            return True
        return False

    def path(self):
        return self._path

    def exists(self):
        from .io import exists
        return exists(self.abs().str())

    def remove(self):
        if self.exists():
            os.remove(self.abs().str())

    def __str__(self):
        return self.str()

    def __eq__(self, other):
        return self.str() == other.str()

    def replace_extension(self, ext):
        n = self.clone()
        basename = self.basename()

        n._name = '%s.%s' % (basename, ext)
        return n

    def extension(self):
        parts = self._name.split('.')
        if len(parts) == 1: return None
        return parts[-1]

    def basename(self, wo_extension=True):
        fname = os.path.basename(self._name)
        if wo_extension and '.' in self._name:
            return '.'.join(fname.split('.')[:-1])

        return fname

    def read(self, *args, **kwargs):
        return read(self.str(), *args, **kwargs)

    def write(self, data, *args, **kwargs):
        self._path.mkdir()
        write(self.str(), data, *args, **kwargs)
        return self

    def add_suffix(self, ext, sep=''):
        """ prepend_extension(ext):
        E.g. Path('/a/b/f.e').prepend_extension('x') returns '/a/b/f.x.e'
        """
        n = self.clone()

        parts = n._name.split('.')
        if len(parts) == 1:
            n._name = '%s%s%s' % (n._name, sep, ext)
        else:
            n._name = '.'.join(parts[:-1])
            n._name += sep + ext + '.' + parts[-1]

        return n

    def str_index(self):
        """ str_id():
        E.g. Path('/a/b/f0000.e').str_id() returns '0000'
        """
        m = rx_id.search(self._name)
        if not m: return None
        return m.group(0)

    def index(self):
        """ str_id():
        E.g. Path('/a/b/f0000.e').str_id() returns 0
        """
        x = self.str_index()
        if x is None: return -1
        return int(x)

    def clone(self):
        return deepcopy(self)

    def copy_to(self, other, follow_symlinks=False):
        from .path import Path

        if isinstance(other, str):
            other = File(other)

        src_name = self.abs().str()
        if isinstance(other, File):
            other.path().mkdir()
        elif isinstance(other, Path):
            other.mkdir()
            other = File(self._name, other)
        dst_name = other.abs().str()
        if os.path.exists(dst_name):
            os.remove(dst_name)
        shutil.copyfile(src_name, dst_name, follow_symlinks=follow_symlinks)
