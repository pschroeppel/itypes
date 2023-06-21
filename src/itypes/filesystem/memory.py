#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

import io
from collections import OrderedDict
from .path import Path
from .file import File


class _DataItem:
    def __init__(self, data=None):
        self._data = data

    def open(self, mode):
        if 'w' in mode:
            if 'a' in mode:
                raise NotImplementedError
            if 'b' in mode:
                data = io.BytesIO()
            else:
                data = io.StringIO()
            data.close = lambda: None
            self._data = data
            return data

        if 'r' in mode:
            if self._data is None:
                raise Exception("Tried to read from None _DataItem")
            if 'b' in mode:
                data = io.BytesIO(self.data())
            else:
                data = io.StringIO(self.data())
            return data

    def finalize(self):
        self._data = self.data()

    def data(self):
        if hasattr(self._data, 'getvalue'): return self._data.getvalue()
        return self._data

    def __len__(self):
        return len(self.data())


def _read_file(file):
    f = file.open('rb')
    return _DataItem(f.read())


def _write_file(file, data):
    file.path().mkdir()
    data = data.data()
    if isinstance(data, str):
        f = file.open('w')
        f.write(data)
    else:
        f = file.open('wb')
        f.write(data)


def _finalize(entries):
    for entry, value in entries.items():
        if isinstance(value, OrderedDict):
            _finalize(value)
        else:
            value.finalize()


def _read(path):
    entries = OrderedDict()
    for dir in path.list_dirs():
        entries[dir.name()] = _read(dir)
    for file in path.list_files():
        entries[file.name()] = _read_file(file)
    return entries


def _write(path, entries):
    for entry, value in entries.items():
        if isinstance(value, OrderedDict):
            _write(path.cd(entry), value)
        else:
            _write_file(path.file(entry), value)

def _lookup(entries, parts):
    if len(parts) == 0:
        return entries

    key = parts[0]
    if key in entries.keys():
        entries = entries[key]
        return _lookup(entries, parts[1:])

    else:
        raise KeyError(parts[0])


def _write_memory(entries, parts, data):
    key = parts[0]

    if len(parts) == 1:
        entries[key] = data
        return

    if not key in entries.keys():
        entries[key] = OrderedDict()

    _write(entries[key], parts[1:], data)

class MemoryFileSystem:
    def __init__(self, mountpoint=None):
        self._entries = OrderedDict()
        self.mount(mountpoint)

    def finalize(self):
        _finalize(self._entries)
        return self

    def read_from_disk(self, path):
        path = Path(path)
        self._entries = _read(path)
        return self

    def mount(self, mountpoint):
        self.unmount()
        if mountpoint is None:
            return
        self._mountpoint = mountpoint
        self._register()
        return self

    def unmount(self):
        self._mountpoint = '/'
        self._unregister()
        return self

    def includes(self, path):
        path = str(path)
        if path.startswith(self._mountpoint):
            return True
        return False

    def mkdir(self, path):
        pass

    def _register(self):
        from .io import register_file_system
        register_file_system(self)
        return self

    def _unregister(self):
        from .io import unregister_file_system
        unregister_file_system(self)
        return self

    def __getitem__(self, file):
        file = str(file)

        if not file.startswith(self._mountpoint):
            raise KeyError(file)
        local_path = file.replace(self._mountpoint, '')

        parts = local_path.split('/')
        data = _lookup(self._entries, parts[1:]).data()
        return data

    def __contains__(self, file):
        try:
            data = self[file]
        except KeyError:
            return False
        return True

    def __setitem__(self, file, data):
        file = str(file)

        if not file.startswith(self._mountpoint):
            raise KeyError(file)
        local_path = file.replace(self._mountpoint, '')

        parts = local_path.split('/')
        _write_memory(self._entries, parts[1:], _DataItem(data))

    def read(self, file):
        file = File(file)
        return self[file]

    def write(self, file, data):
        file = File(file)
        self[file] = data

    def write_to_disk(self, path):
        path = Path(path)
        _write(path, self._entries)
        return self

    def __str__(self):
        str = ""
        for entry, value in self._entries.items():
            if isinstance(value, OrderedDict):
                str += f"DIR  {' '*8} {entry}"
            else:
                str += f"FILE {len(value):8d} {entry}"
            str += "\n"
        return str