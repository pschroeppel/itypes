#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

_visualization_types = {}
def register_visualization(type, visualization_class):
    global _visualization_types
    _visualization_types[type] = visualization_class

def _instantiate_visualization(ds, path, type, **kwargs):
    global _visualization_types

    if type not in _visualization_types:
        raise Exception(f"Unknown visualization type: \"{type}\"")

    viz = _visualization_types[type](ds, path)

    kwargs["type"] = type
    viz.create(**kwargs)

    return viz

def _reinstantiate_visualization(ds, path):
    global _visualization_types

    reg = ds._reg
    type = reg[path + "type"]

    if type not in _visualization_types:
        raise Exception(f"Unknown visualization type: \"{type}\"")

    return _visualization_types[type](ds, path=path)
