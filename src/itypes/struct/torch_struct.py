#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

from .numpy_struct import NumpyStruct
from ..type import is_numpy, is_torch


class TorchStruct(NumpyStruct):
    def clone_type(self, *args, **kwargs):
        return TorchStruct(*args, dims=self.dims, **kwargs)

    def clone(self, clone_functions=None):
        if clone_functions is None:
            clone_functions = []
        clone_functions.append((is_torch, lambda x: x.clone()))
        return super().clone(clone_functions)

    def translate_tensors(self, func, *args, **kwargs):
        def _translate(x, *args, **kwargs):
            if is_torch(x):
                x = func(x, *args, **kwargs)
            return x
        return self.translate(_translate, *args, **kwargs)

    def apply_tensors(self, func, *args, **kwargs):
        def _apply(x):
            if is_torch(x):
                func(x, *args, **kwargs)
        self.apply(_apply, *args, **kwargs)

    def read(self, member, filename, dtype=None, device=None):
        from ..filesystem import File
        self[member] = File(filename).read(dtype=dtype, device=device, dims=self.dims)

    def detach(self):
        return self.translate_tensors(lambda x: x.detach())

    def to(self, device):
        import torch
        def _translate(x):
            if is_torch(x):
                if device == 'numpy':
                    x = x.cpu().detach().numpy()
                else:
                    x = x.to(device)
            elif is_numpy(x):
                if device != 'numpy':
                    x = torch.from_numpy(x).to(device)
            return x

        return self.translate(_translate)

    def to_numpy(self):
        return self.to('numpy')

    def _is_data(self, x):
        return is_numpy(x) or is_torch(x)

    def _data_nan_to_num(self, x):
        if is_numpy(x): return super()._data_nan_to_num(x)
        else:           return x.nan_to_num()

    def _concat_data(self, x):
        import torch
        if is_numpy(x[0]): return super()._concat_matrices(x)
        else:              return torch.cat(x)

    def _data_expand_dims(self, x):
        if is_numpy(x): return super()._data_expand_dims(x)
        else:           return x.unsqueeze(0)

    def _data_permute_dims(self, x, dims):
        if is_numpy(x): return super()._data_permute_dims(x, dims)
        else:           return x.permute(dims)
