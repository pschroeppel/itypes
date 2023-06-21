#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

import numpy as np

from ..type import is_numpy
from .data_struct import DataStruct


class NumpyStruct(DataStruct):
    def clone_type(self, *args, **kwargs):
        return NumpyStruct(*args, dims=self.dims, *kwargs)

    def clone(self, clone_functions=None):
        if clone_functions is None:
            clone_functions = []
        clone_functions.append((is_numpy, lambda x: x.copy()))
        return super().clone(clone_functions)

    def translate_arrays(self, func, *args, **kwargs):
        def _translate(x, *args, **kwargs):
            if is_numpy(x):
                x = func(x, *args, **kwargs)
            return x
        return self.translate(_translate, *args, **kwargs)

    def apply_arrays(self, func, *args, **kwargs):
        def _apply(x):
            if is_numpy(x):
                func(x, *args, **kwargs)
        self.apply(_apply, *args, **kwargs)

    def read(self, member, filename, dtype=None):
        from ..filesystem import File
        self[member] = File(filename).read(dtype=dtype, device="numpy", dims=self.dims)

    def write(self, member, filename):
        from ..filesystem import File
        File(filename).write(dims=self.dims)

    def _is_data(self, x):
        return is_numpy(x)

    def _data_nan_to_num(self, x):
        return np.nan_to_num(x)

    def _concat_data(self, x):
        return np.concatenate(x)

    def _data_expand_dims(self, x):
        return np.expand_dims(x, 0)

    def _concat_data(self, x):
        return np.concatenate(x)

    def _data_permute_dims(self, x, dims):
        return np.transpose(x, dims)

