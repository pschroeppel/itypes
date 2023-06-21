#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

import os
import io
import sys
import re
import numpy as np
from collections import OrderedDict

#
# ----------- Type Registry -----------
#
from ..conversion import convert_dims, convert_device, convert_dtype

_read_functions = {}
_write_functions = {}

def is_list(x):
    if isinstance(x, list) or isinstance(x, tuple):
        return True
    return False

def register_read_function(ext, func, type=""):
    global _read_functions
    if is_list(ext):
        for ent in ext:
            register_read_function(ent, func, type)
    else:
        _read_functions[ext] = (type, func)

def register_write_function(ext, func, type=""):
    global _write_functions
    if is_list(ext):
        for ent in ext:
            register_write_function(ent, func, type)
    else:
        _write_functions[ext] = (type, func)

# Memory filesystems
_filesystems = []

def register_file_system(filesystem):
    global _filesystems
    if filesystem not in _filesystems:
        _filesystems.append(filesystem)

def unregister_file_system(filesystem):
    global _filesystems
    if filesystem in _filesystems:
        _filesystems.remove(filesystem)

def _open(filename, mode):
    global _filesystems

    if 'w' in mode:
        for fs in _filesystems:
            if fs.includes(filename):
                if 'a' in mode:
                    raise NotImplementedError
                if 'b' in mode: data = io.BytesIO()
                else: data = io.StringIO()
                data.close = lambda: None
                fs[filename] = data
                return data

    if 'r' in mode:
        for fs in _filesystems:
            if fs.includes(filename):
                if 'b' in mode: data = io.BytesIO(fs[filename])
                else: data = io.StringIO(fs[filename])
                return data

    return open(filename, mode)

def _open_file_for_reading(filename, binary=True):
    global _filesystems
    for fs in _filesystems:
        if fs.includes(filename):
            data = fs[filename]
            return io.BytesIO(data)

    return open(filename, "r" if not binary else "rb")

def _write_file(filename, data, binary=True):
    global _filesystems
    for fs in _filesystems:
        if fs.includes(filename):
            fs[filename] = data
            return

    open(filename, "w" if not binary else "wb").write(data)

def _is_filesystem_file(filename): 
    global _filesystems
    for fs in _filesystems:
        if fs.includes(filename):
            return True
        
    return False 

def mkdirs(path):
    global _filesystems
    for fs in _filesystems:
        if fs.includes(path):
            fs.mkdir(path)
            return

    from pathlib import Path
    Path(path).mkdir(parents=True, exist_ok=True)
    return path

def exists(filename):
    global _filesystems
    for fs in _filesystems:
        if filename in fs:
            return True

    return os.path.exists(filename)

def is_dir(filename):
    global _filesystems
    for fs in _filesystems:
        if filename in fs:
            return True

    return os.path.isdir(filename)


#
# ----------- Proxy Functions -----------
#
def read(file, *args, **kwargs):
    global _read_functions
    from .file import File

    # Make sure file is a file
    file = File(file)

    # Get extension
    ext = file.extension()
    if ext not in _read_functions:
        raise Exception(f"Don't know how to read extension '{ext}'")

    # Get type and function
    type, func = _read_functions[ext]

    # Process arguments for specific type
    if "image" in type:
        alpha = kwargs.pop("alpha", None)

    if "data" in type:
        dtype = kwargs.pop("dtype", None)
        dims = kwargs.pop("dims", "hwc")
        device = kwargs.pop("device", "numpy")

    # Low-level read
    value = func(file.abs().str(), *args, **kwargs)

    # Post-process
    if "image" in type:
        # Ensure we have three dimensions (hwc)
        if len(value.shape) == 2:
            value = np.expand_dims(value, 2)

        # Correct the alpha channel if alpha=True or alpha=False is given
        if alpha is True:
            if value.shape[2] == 1:
                value = np.concatenate((value, np.ones(value.shape, dtype=value.dtype)), axis=2)
            if value.shape[2] == 3:
                value = np.concatenate((value, np.ones((value.shape[0], value.shape[1], 1), dtype=value.dtype)), axis=2)
        if alpha is False:
            if value.shape[2] == 2:
                value = value[:, :, 0:1]
            if value.shape[2] == 4:
                value = value[:, :, 0:3]

    if "data" in type:
        value = convert_dtype(value, dtype)
        value = convert_dims(value, "hwc", dims)
        value = convert_device(value, device)

    return value

def write(file, data, *args, **kwargs):
    global _write_functions
    from .file import File

    # Make sure file is a file
    file = File(file)

    ext = file.extension()
    if ext is None: ext='txt' # If we don't have an extension, we assume a text file
    if ext not in _write_functions:
        raise Exception(f"Don't know how to write extension '{ext}'")

    type, func = _write_functions[ext]

    if "data" in type:
        data = convert_device(data, "numpy")
        if "dims" in kwargs:
            dims = kwargs.pop("dims")
            data = convert_dims(data, dims, "hwc")

    value = func(file.abs().str(), data, *args, **kwargs)

    return value


#
# ----------- Pickle (.p) -----------
#

def read_pickle(filename):
    f = _open_file_for_reading(filename)
    import pickle
    return pickle.load(f)

register_read_function('p', read_pickle)

def write_pickle(filename, data):
    f = io.BytesIO()
    import pickle
    pickle.dump(data, f)
    _write_file(filename, f.getvalue())

register_write_function('p', write_pickle)


#
# ----------- Numpy (.np, .npy) -----------
#

def read_numpy(filename):
    f = _open_file_for_reading(filename)
    return np.load(f, allow_pickle=True)

register_read_function(('np', 'npy'), read_numpy)

def write_numpy(filename, data):
    f = io.BytesIO()
    np.save(f, data, allow_pickle=True)
    _write_file(filename, f.getvalue())

register_write_function(('np', 'npy'), write_numpy)


#
# ----------- Compressed Numpy (.npz) -----------
#

def read_numpy_compressed(filename):
    f = _open_file_for_reading(filename)
    return np.load(f, allow_pickle=True)['arr_0']

register_read_function('npz', read_numpy_compressed)

def write_numpy_compressed(filename, data):
    f = io.BytesIO()
    np.savez_compressed(f, data, allow_pickle=True)
    _write_file(filename, f.getvalue())

register_write_function('npz', write_numpy_compressed)


#
# ----------- Text (.txt) and HTML (.html) -----------
#

def read_text(filename):
    f = _open_file_for_reading(filename, binary=False)
    return f.read()

register_read_function('txt', read_text)
register_read_function('html', read_text)

def write_text(filename, text):
    f = io.StringIO()
    f.write(text)
    _write_file(filename, f.getvalue(), binary=False)

register_write_function('txt', write_text)
register_write_function('html', write_text)


#
# ----------- JSON (.json) -----------
#

def read_json(filename):
    f = _open_file_for_reading(filename, binary=False)
    import json
    return json.load(f, object_pairs_hook=OrderedDict)

register_read_function('json', read_json)

def write_json(filename, data, indent=4):
    f = io.StringIO()
    import json
    json.dump(data, f, indent=indent)
    f.write('\n')
    _write_file(filename, f.getvalue(), binary=False)

register_write_function('json', write_json)


#
# ----------- Image (.exr) -----------
#

def read_exr(filename):
    if _is_filesystem_file(filename): 
        raise NotImplementedError("read_exr() does not support memory filesystems")
    
    import OpenEXR, Imath
    pt = Imath.PixelType(Imath.PixelType.FLOAT)
    file = OpenEXR.InputFile(filename)
    dw = file.header()['dataWindow']
    w, h = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)
    channels = file.header()['channels'].keys()

    if len(channels) == 1:
        ch = 'R' if 'R' in channels else 'Y'
        data = np.fromstring(file.channel(ch, pt), dtype=np.float32)
        data.shape = (h, w)

    elif len(channels) >= 3:
        data = np.zeros((h, w, len(channels)), dtype=np.float32)

        red = np.frombuffer(file.channel('R', pt), dtype=np.float32)
        red.shape = (h, w)
        data[:, :, 0] = red

        green = np.frombuffer(file.channel('G', pt), dtype=np.float32)
        green.shape = (h, w)
        data[:, :, 1] = green

        blue = np.frombuffer(file.channel('B', pt), dtype=np.float32)
        blue.shape = (h, w)
        data[:, :, 2] = blue

    else:
        raise Exception(f"Don't know how to read EXR with {channels} channels")

    return data

register_read_function('exr', read_exr, type='data,image')

def write_exr(filename, data):
    if _is_filesystem_file(filename): 
        raise NotImplementedError("write_exr() does not support memory filesystems")

    import OpenEXR
    data = convert_dtype(data, np.float32)
    if len(data.shape) == 3 and data.shape[2] == 3:
        data = data.astype(np.float32)
        h, w, c = data.shape
        d = {}
        d["R"] = data[:, :, 0].tostring()
        if c > 1:
            d["G"] = data[:, :, 1].tostring()
        if c > 2:
            d["B"] = data[:, :, 2].tostring()

        exr = OpenEXR.OutputFile(filename, OpenEXR.Header(w, h))
        exr.writePixels(d)

    elif len(data.shape) == 2 or (len(data.shape) == 3 and data.shape[2] == 1):
        data = data.squeeze()

        h, w = data.shape
        exr = OpenEXR.OutputFile(filename, OpenEXR.Header(w, h))
        exr.writePixels({"R": data.tostring()})

    else:
        raise Exception(f"Don't know how to write EXR with {data.shape} dimensions")

register_write_function('exr', write_exr, type='data,image')


#
# ----------- Image (.jpg, .png, .bmp, .tif) -----------
#

def read_image(filename):
    f = _open_file_for_reading(filename)

    from PIL import Image

    value = np.asarray(Image.open(f))

    # Fix PIL bug on reading 16 bit as 32
    if value.dtype == np.int32:
        value = value.astype(np.uint16)

    return value

register_read_function(('jpg', 'png', 'bmp', 'tif'), read_image, type='data,image')

def write_image(filename, data):
    f = io.BytesIO()

    from PIL import Image

    # Convert data type
    if data.dtype == np.uint8 or data.dtype == np.uint16:
        pass
    else:
        data = convert_dtype(data, np.uint8)

    # Remove additional dimensions
    data = data.squeeze()

    from .file import File
    file = File(filename)
    format = file.extension()

    Image.fromarray(data).save(f, compress_level=1, format=format)

    _write_file(filename, f.getvalue())

register_write_function(('jpg', 'png', 'bmp', 'tif'), write_image, type='data,image')


#
# ----------- Image (.pfm) -----------
#

def read_pfm(file):
    f = _open_file_for_reading(file)

    header = f.readline().rstrip()
    if header.decode("ascii") == 'PF':
        color = True
    elif header.decode("ascii") == 'Pf':
        color = False
    else:
        raise Exception('Not a PFM file.')

    dim_match = re.match(r'^(\d+)\s(\d+)\s$', f.readline().decode("ascii"))
    if dim_match:
        width, height = list(map(int, dim_match.groups()))
    else:
        raise Exception('Malformed PFM header.')

    scale = float(f.readline().decode("ascii").rstrip())
    if scale < 0: # little-endian
        endian = '<'
        scale = -scale
    else:
        endian = '>' # big-endian

    data = np.fromfile(f, endian + 'f')
    shape = (height, width, 3) if color else (height, width, 1)

    data = np.reshape(data, shape)
    data = np.flipud(data)

    return data * scale

register_read_function('pfm', read_pfm, type='data,image')

def write_pfm(filename, image, scale=1):
    file = io.BytesIO()

    if image.dtype == np.float64:
        image = image.astype(np.float32)

    if image.dtype != np.float32:
        raise Exception('Image dtype must be float32.')

    image = np.flipud(image)

    if len(image.shape) == 3 and image.shape[2] == 3: # color image
        color = True
    elif len(image.shape) == 2 or len(image.shape) == 3 and image.shape[2] == 1: # greyscale
        color = False
    else:
        raise Exception('Image must have H x W x 3, H x W x 1 or H x W dimensions.')

    file.write('PF\n' if color else 'Pf\n'.encode())
    file.write('%d %d\n'.encode() % (image.shape[1], image.shape[0]))

    endian = image.dtype.byteorder

    if endian == '<' or endian == '=' and sys.byteorder == 'little':
        scale = -scale

    file.write('%f\n'.encode() % scale)

    file.write(image.tobytes())
    _write_file(filename, file.getvalue())


register_write_function('pfm', write_pfm, type='data,image')


#
# ----------- Image (.pfm) -----------
#

def read_flow(name):
    f = _open_file_for_reading(name)

    header = f.read(4)
    if header.decode("utf-8") != 'PIEH':
        raise Exception('Flow file header does not contain PIEH')

    width = np.fromfile(f, np.int32, 1).squeeze()
    height = np.fromfile(f, np.int32, 1).squeeze()

    flow = np.fromfile(f, np.float32, width * height * 2).reshape((height, width, 2))

    return flow.astype(np.float32)

register_read_function('flo', read_flow, type='data, flow')

def write_flow(filename, flow):
    f = io.BytesIO()

    if flow.dtype == np.float64:
        flow = flow.astype(np.float32)

    if flow.dtype != np.float32:
        raise Exception('Flow dtype must be float32.')

    f.write('PIEH'.encode('utf-8'))
    f.write(np.array([flow.shape[1], flow.shape[0]], dtype=np.int32).tobytes())
    flow = flow.astype(np.float32)
    f.write(flow.tobytes())
    _write_file(filename, f.getvalue())

register_write_function('flo', write_flow, type='data, flow')


#
# ----------- Blob (.blob) -----------
#

def read_blob(name):
    f = _open_file_for_reading(name)

    if(f.readline().decode("utf-8"))  != 'float32\n':
        raise Exception('float file %s did not contain <float32> keyword' % name)

    dim = int(f.readline())

    dims = []
    count = 1
    for i in range(0, dim):
        d = int(f.readline())
        dims.append(d)
        count *= d

    dims = list(reversed(dims))

    # This is to ensure you can do direct writes from C++
    data = np.fromfile(f, np.float32, count).reshape(dims)
    if dim == 2:
        data = np.transpose(data, (0, 1))
    elif dim == 3:
        data = np.transpose(data, (1, 2, 0))
    elif dim == 4:
        data = np.transpose(data, (2, 3, 1, 0))
    else:
        raise Exception('bad float file dimension: %d' % dim)

    return data

register_read_function('blob', read_blob, type='data')

def write_blob(filename, data):
    f = io.BytesIO()

    if data.dtype == np.float64:
        flow = data.astype(np.float32)

    if data.dtype != np.float32:
        raise Exception('Blob dtype must be float32.')

    dim = len(data.shape)

    f.write(('float32\n').encode('ascii'))
    f.write(('%d\n' % dim).encode('ascii'))

    if dim == 1:
        f.write(('%d\n' % data.shape[0]).encode('ascii'))
    else:
        f.write(('%d\n' % data.shape[1]).encode('ascii'))
        f.write(('%d\n' % data.shape[0]).encode('ascii'))
        for i in range(2, dim):
            f.write(('%d\n' % data.shape[i]).encode('ascii'))

    # This is to ensure you can do direct writes from C++
    data = data.astype(np.float32)
    if dim == 2:
        f.write(data.tobytes())
    elif dim == 3:
        f.write(np.transpose(data, (2, 0, 1)).tobytes())
    elif dim == 4:
        f.write(np.transpose(data, (3, 2, 0, 1)).tobytes())
    else:
        raise Exception('bad float file dimension: %d' % dim)

    _write_file(filename, f.getvalue())

register_write_function('blob', write_blob, type='data')



