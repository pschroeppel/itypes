#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

from ..type import is_dict, is_list, is_numpy, is_torch, is_value, is_str


def _translate(x, func, *args, **kwargs):
    def _recurse(value):
        if is_dict(value) and hasattr(value, 'translate'):
            value = value.translate(func, *args, **kwargs)
        else:
            value = _translate(value, func, *args, **kwargs)
        return value

    if is_dict(x):
        if hasattr(x, 'clone_type'): y = x.clone_type()
        else:                        y = type(x)()
        for key, value in x.items():
            if not key.startswith("_"):
                y[key] = _recurse(value)
        if 'dims' in kwargs:
            y.dims = kwargs["dims"]
    elif is_list(x):
        y = []
        for i in range(0, len(x)):
            value = _recurse(x[i])
            y.append(value)
    else:
        if is_list(func):
            y = x
            for check, translator in func:
                if check(x):
                    y = translator(x, *args, **kwargs)
                    break
        else:
            y = func(x, *args, **kwargs)

    return y

def _create_empty(x, template=None):
    def _recurse(value, template=None):
        if is_dict(value) and hasattr(value, 'create_empty'):
            value = value.create_empty(template)
        else:
            value = _create_empty(value, template)
        return value

    if is_dict(x):
        if template is not None:       y = _translate(template, lambda x: x)
        elif hasattr(x, 'clone_type'): y = x.clone_type()
        else:                          y = type(x)()
        for key, value in x.items():
            if key.startswith("_"):
                continue
            if template is not None and key in template:
                value = _recurse(value, y[key])
            else:
                value = _recurse(value)
            y[key] = value
        if 'dims' in x:
            y.dims = x["dims"]
    elif is_list(x):
        y = []
        for i in range(0, len(x)):
            if template is not None and i in template:
                value = _recurse(x[i], template[i])
            else:
                value = _recurse(x[i])
            y.append(value)
    else:
        y = template

    return y

def _apply(x, func, *args, **kwargs):
    if is_dict(x):
        for key, value in x.items():
            if is_dict(value) and hasattr(value, 'apply'):
                value.apply(func, *args, **kwargs)
            else:
                _apply(value, func, *args, **kwargs)
    elif is_list(x):
        for i in range(0, len(x)):
            _apply(x[i], func, *args, **kwargs)
    else:
        func(x, *args, **kwargs)

class KeyPath(list):
    def __repr__(self):
        str_path = [str(x) for x in self]
        str_path = '.'.join(str_path)
        while '.[' in str_path:
            str_path = str_path.replace('.[', '[')
        return str_path

    def first(self):
        return self[0]

    def last(self):
        return self[-1]

    def is_empty(self):
        return len(self) == 0

    def append_back(self, value):
        subpath = KeyPath()
        for x in self:
            subpath.append(x)
        subpath.append(value)
        return subpath

    def remove_first(self):
        subpath = KeyPath()
        for x in self[1:]:
            subpath.append(x)
        return subpath

    def get(self, struct):
        if len(self) == 1:
            return struct[self[0].value]

        sub_path = self.remove_first()
        return sub_path.get(struct[self[0].value])

    def set(self, struct, value):
        if len(self) == 1:
            if is_list(struct) and self[0].value >= len(struct):
                struct.append(self[0].value)
            else:
                struct[self[0].value] = value
            return

        sub_path = self.remove_first()
        struct = struct[self[0].value]
        return sub_path.set(struct, value)


class DictKey:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return str(self.value)

class ListKey:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return '[' + str(self.value) + ']'

def _flatten_keys(x, path, result):
    if path is None: path = KeyPath()
    if result is None: result = []

    if is_dict(x):
        for key, value in x.items():
            subpath = path.append_back(DictKey(key))
            _flatten_keys(value, subpath, result)
    elif is_list(x):
        for i in range(0, len(x)):
            subpath = path.append_back(ListKey(i))
            _flatten_keys(x[i], subpath, result)
    else:
        result.append(path)

    return result

def _flatten(x, path, result):
    if path is None: path = KeyPath()

    if is_dict(x):
        for key, value in x.items():
            subpath = path.append_back(DictKey(key))
            _flatten(value, subpath, result)
    elif is_list(x):
        for i in range(0, len(x)):
            subpath = path.append_back(ListKey(i))
            _flatten(x[i], subpath, result)
    else:
        result[str(path)] = x

def _common_keys(structs, subset=False):
    flat_keys = [s.flat_keys() for s in structs]
    common_keys = []
    for key in flat_keys[0]:
        found = True
        for s in structs:
            if key not in s:
                found = False
                break
        if found:
            common_keys.append(key)
        else:
            if not subset:
                raise Exception(f"Key '{key}' is not provided by all structs")

    return common_keys

def _value_to_str(value):
    result = ""

    if is_torch(value):
        result += ('tensor, shape=%s, dtype=%s, device=%s' % (list(value.shape), value.dtype, value.device))
        if value.grad_fn is not None:
            result += ", grad_fn=%s" % value.grad_fn
    elif is_numpy(value):
        result += ('ndarray, shape=%s, dtype=%s' % (value.shape, value.dtype))
    elif is_str(value):
        result += ('\'%s\'' % (value))
    else:
        result += ('%s' % (value))

    return result

def _list_to_str(list, indent=0):
    result = []
    prefix = ' ' * (indent * 4)

    for key, value in enumerate(list):
        if is_value(value):
            result.append((prefix + str(key), _value_to_str(value)))
        else:
            result.append((prefix + str(key),''))
            if is_dict(value):
                result += _dict_to_str(value, indent + 1)
            elif is_list(value):
                result += _list_to_str(value, indent + 1)

    return result

def _dict_to_str(struct, indent=0):
    result = []
    prefix = ' ' * (indent * 4)

    for key, value in struct.items():
        if is_value(value):
            result.append((prefix + str(key), _value_to_str(value)))
        else:
            result.append((prefix + str(key),''))
            if is_dict(value):
                result += _dict_to_str(value, indent + 1)
            elif is_list(value):
                result += _list_to_str(value, indent + 1)

    return result