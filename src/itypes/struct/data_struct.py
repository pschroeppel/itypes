#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

from ..type import is_list, is_dict
from .struct import Struct
from .helper import _common_keys


class DataStruct(Struct):
    def __init__(self, *args, dims=None, **kwargs):
        super().__init__(*args, **kwargs)
        if dims is not None:
            self.dims = dims

    def clone_type(self):
        return DataStruct(dims=self.dims)

    def translate_data(self, func, *args, **kwargs):
        def _translate(x, *args, **kwargs):
            if self._is_data(x):
                x = func(x, *args, **kwargs)
            return x
        return self.translate(_translate, *args, **kwargs)

    def apply_data(self, func, *args, **kwargs):
        def _apply(x):
            if self._is_data(x):
                func(x, *args, **kwargs)
        self.apply(_apply, *args, **kwargs)

    def nan_to_num(self):
        def _convert(x):
            return self._data_nan_to_num(x)
        return self.translate_data(_convert)

    def to_hwc(self):
        old_dims = self.dims

        def _to_hwc(x, dims):
            if len(x.shape) == 2:
                x = self._data_expand_dims(x)
            if len(x.shape) == 4:
                if x.shape[0] != 1:
                    raise Exception("to_hwc() error: batch dimension is greater than 1")
                x = x[0, ...]
            if len(x.shape) == 3 and "hwc" not in old_dims:
                x = self._data_permute_dims(x, (1, 2, 0))
            return x

        return self.translate_data(_to_hwc, dims="hwc")

    def to_chw(self):
        old_dims = self.dims

        def _to_chw(x, dims):
            if len(x.shape) == 2:
                x = self._data_expand_dims(x)
            if len(x.shape) == 4:
                if x.shape[0] != 1:
                    raise Exception("to_chw() error: batch dimension is greater than 1")
                x = x[0, ...]
            if len(x.shape) == 3 and "chw" not in old_dims:
                x = self._data_permute_dims(x, (2, 0, 1))
            return x

        return self.translate_data(_to_chw, dims="chw")

    def to_bhwc(self):
        old_dims = self.dims

        def _to_bhwc(x, dims):
            if len(x.shape) == 2:
                x = self._data_expand_dims(x)
            if len(x.shape) == 3:
                x = self._data_expand_dims(x)
            if len(x.shape) == 4 and "hwc" not in old_dims:
                x = self._data_permute_dims(x, (0, 2, 3, 1))
            return x

        return self.translate_data(_to_bhwc, dims="bhwc")

    def to_bchw(self):
        old_dims = self.dims

        def _to_bchw(x, dims):
            if len(x.shape) == 2:
                x = self._data_expand_dims(x)
            if len(x.shape) == 3:
                x = self._data_expand_dims(x)
            if len(x.shape) == 4 and "chw" not in old_dims:
                x = self._data_permute_dims(x, (0, 3, 1, 2))
            return x

        return self.translate_data(_to_bchw, dims="bchw")

    def concat_batch(self, inputs):
        flat_keys = _common_keys(inputs)

        result = inputs[0].create_empty()
        for key in flat_keys:
            members = []
            for input in inputs:
                members.append(input[key])

            if str(key.last()) == 'dims':
                dims = members[0]
                for member in members:
                    if member != dims:
                        raise Exception("concat_batch() tensor dims don't agree")
                result.dims = dims
            elif self._is_data(members[0]):
                result[key] = self._concat_data(members)
            else:
                result[key] = members

        return result

    def split_batch(self):
        # Determine batch size
        batch_size = None
        def _test_bs(x):
            nonlocal batch_size
            new_batch_size = x.shape[0]
            if batch_size is not None and batch_size != new_batch_size:
                raise Exception(f"split_batch() found inconsistent batch dimensions {batch_size} and {new_batch_size}")
            batch_size = new_batch_size
        self.apply_data(_test_bs)

        if batch_size is None:
            raise Exception('split_batch() could not find any batch dimension')

        # Extract structures for each batch entry
        result = []
        for idx in range(0, batch_size):
            def _extract_batch(x):
                nonlocal idx
                if self._is_data(x):
                    if len(x.shape) == 4:
                        exp = self._data_expand_dims(x[idx, ...])
                        return exp
                elif is_list(x):
                    return x[idx]
                else:
                    return x

            def _translate(x):
                if is_dict(x):
                    if hasattr(x, 'clone_type'): y = x.clone_type()
                    else:                        y = type(x)()
                    for key, value in x.items():
                        y[key] = _translate(value)
                else:
                    y = _extract_batch(x)
                return y

            entry = _translate(self)
            result.append(entry)

        return result

    def _is_data(self, x): raise NotImplementedError
    def _data_nan_to_num(self, x): raise NotImplementedError
    def _concat_data(self, x): raise NotImplementedError
    def _data_expand_dims(self, x): raise NotImplementedError
    def _data_permute_dims(self, x, dims): return NotImplementedError
