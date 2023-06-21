#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

from .type import is_numpy, is_torch


def convert_dims(data, old, new):
    import numpy as np

    if data is None or old == new:
        return data

    if old not in ["hwc", 'chw', "bhwc", "bchw"]:
        raise Exception("Old dimensions must be one of hwc, chw, bhwc, bchw")

    if new not in ["hwc", 'chw', "bhwc", "bchw"]:
        raise Exception("New dimensions must be one of hwc, chw, bhwc, bchw")

    def _expand_dims(x):
        if is_numpy(x):
            return np.expand_dims(x, 0)
        else:
            return x.unsqueeze(0)

    def _permute(x, order):
        if is_numpy(x):
            return np.transpose(x, order)
        else:
            return x.permute(order)

    # Ensure we have at least 3 dimensions
    while len(data.shape) < 3:
        data = _expand_dims(data)

    if old == "chw":
        if new == "hwc":
            return _permute(data, (1, 2, 0))
        elif new == "bhwc":
            return _expand_dims(_permute(data, (1, 2, 0)))
        elif new == "bchw":
            return _expand_dims(data)
    elif old == "hwc":
        if new == "chw":
            return _permute(data, (2, 0, 1))
        elif new == "bhwc":
            return _expand_dims(data)
        elif new == "bchw":
            return _expand_dims(_permute(data, (2, 0, 1)))
    elif old == "bchw":
        if new == "hwc":
            return _permute(data[0, ...], (1, 2, 0))
        elif new == "chw":
            return data[0, ...]
        elif new == "bhwc":
            return _permute(data, (0, 2, 3, 1))
    elif old == "bhwc":
        if new == "hwc":
            return data[0, ...]
        elif new == "chw":
            return _permute(data[0, ...], (2, 0, 1))
        elif new == "bchw":
            return _permute(data, (0, 3, 1, 2))

    # We should have returned already
    raise Exception("Invalid state encountered")

def convert_dtype(data, new):
    if data is None or new is None:
        return data

    import numpy as np

    if is_torch(data):
        import torch
        torch_to_numpy_dtype_dict = {
            torch.bool: bool,
            torch.uint8: np.uint8,
            torch.int8: np.int8,
            torch.int16: np.int16,
            torch.int32: np.int32,
            torch.int64: np.int64,
            torch.float16: np.float16,
            torch.float32: np.float32,
            torch.float64: np.float64,
        }
        old = torch_to_numpy_dtype_dict[data.dtype]
    else:
        old = data.dtype

    if old == new:
        return data

    if old not in [np.float32, np.float64, np.uint8, np.uint16, np.int32, bool]:
        raise Exception("Old dtype must be one of float32, float64, uint8, uint16, bool")

    if new not in [np.float32, np.float64, np.uint8, np.uint16, bool]:
        raise Exception("Old dtype must be one of float32, float64, uint8, uint16, bool")

    def _convert_type(x, type):
        if is_torch(x):
            import torch
            numpy_to_torch_dtype_dict = {
                bool: torch.bool,
                np.uint8: torch.uint8,
                np.int8: torch.int8,
                np.int16: torch.int16,
                np.uint16: torch.int32, # Torch does not support uint16
                np.int32: torch.int32,
                np.int64: torch.int64,
                np.float16: torch.float16,
                np.float32: torch.float32,
                np.float64: torch.float64,
            }
            return x.to(numpy_to_torch_dtype_dict[type])
        else:
            return x.astype(type)

    def _clamp(data):
        if is_torch(data):
            return data.clamp(0, 1)
        else:
            return np.clip(data, 0, 1)

    if old in [np.float32, np.float64]:
        if new in [np.float32, np.float64]:
            return _convert_type(data, new)
        elif new == np.uint8:
            return _convert_type(_clamp(data) * 255.0, np.uint8)
        elif new == np.uint16:
            return _convert_type(_clamp(data) * 65535.0, np.uint16)
        elif new == bool:
            return data > 0.5
    elif old == np.uint8:
        if new in [np.float32, np.float64]:
            return _convert_type(data, new) / 255.0
        elif new == np.uint16:
            return _convert_type(data, np.uint16) * 256
        elif new == bool:
            return data > 256 // 2
    elif old == np.uint16 or old == np.int32:
        if new in [np.float32, np.float64]:
            return _convert_type(data, new) / 65535.0
        elif new == np.uint16 or np.int32:
            return data
        elif new == np.uint8:
            return _convert_type(data / 256, np.uint8)
        elif new == bool:
            return data > 65536 // 2
    elif old == bool:
        if new in [np.float32, np.float64]:
            return _convert_type(data, new)
        elif new == np.uint8:
            return _convert_type(data, np.uint8) * 255
        elif new == np.uint16:
            return _convert_type(data, np.uint16) * 65535

        # We should have returned already
        raise Exception("Invalid state encountered")

def convert_device(data, device):
    if data is None or device is None:
        return data

    if is_numpy(data):
        if device == "numpy":
            return data
        else:
            import torch
            import numpy as np
            # Torch does not support uint16
            data = data.copy()
            if data.dtype == np.uint16:
                data = data.astype(np.int32)
            return torch.from_numpy(data).to(device).detach()
    elif is_torch(data):
        if device == "numpy":
            return data.cpu().detach().numpy()
        else:
            return data.to(device)
    else:
        raise Exception(f"Invalid data of type {type(data)} passed into convert_device()")


def convert(data, dtype=None, device=None, old_dims=None, new_dims=None):
    assert((old_dims is None) == (new_dims is None))

    if device is not None:
        data = convert_device(data, device)
    if old_dims is not None and new_dims is not None:
        data = convert_dims(data, old_dims, new_dims)
    if dtype is not None:
        data = convert_dtype(data, dtype)

    return data