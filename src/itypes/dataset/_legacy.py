#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

from collections import OrderedDict
from ..filesystem import File


def read_gridseq(ds, file):
    with file.open('r') as f:
        lines = f.read().split("\n")

        # Get grid definition
        for line in lines:
            if line.startswith("def"):
                parts = line.split(" ")
                col = int(parts[1])
                row = int(parts[2])
                id = parts[3].replace("<", "").replace(">", "")
                type = parts[4]
                title = None
                if len(parts)>5:
                    title = ' '.join(parts[5:])
                kwargs = {}
                if type == "label":
                    kwargs["text"] = title
                    kwargs["template"] = "<h2>{text}</h2>"
                    type = "text"
                ds.viz.create(type=type, var=id, index=(col, row), **kwargs)

        # Get data definition
        groups = OrderedDict()
        group_counter = 0
        item_counter = 0

        def add(group_name, item_name, fills):
            nonlocal groups
            nonlocal group_counter
            nonlocal item_counter

            if group_name is None:
                group_name = "group%d" % group_counter
                group_counter += 1

            if item_name is None:
                item_name = "item%d" % item_counter
                item_counter += 1

            if group_name not in groups:
                groups[group_name] = OrderedDict()

            groups[group_name][item_name] = fills

        current_entry_name = None
        current_set_name = None
        current_fills = OrderedDict()
        for line in lines:
            parts = line.split(" ")
            if line.startswith("fill"):
                id = parts[1].replace("<", "").replace(">", "")
                if parts[2] == 'None': data_file = None
                else: data_file = File(parts[2])
                current_fills[id] = data_file
            elif line.startswith("set_name"):
                current_set_name = parts[1]
            elif line.startswith("entry_name"):
                current_entry_name = parts[1]
            elif line.startswith("next"):
                add(current_set_name, current_entry_name, current_fills)
                current_fills = OrderedDict()
                current_entry_name = None
                current_set_name = None

        if len(current_fills):
            add(current_set_name, current_entry_name, current_fills)

        for group_name, items in groups.items():
            group = ds.seq.group(group_name)
            for item_name, ids in items.items():
                item = group.item(item_name)
                for id, data_file in ids.items():
                    if data_file is None:
                        item[id].set_data(None)
                    else:
                        item[id].set_ref(file.path() + data_file, check_if_exists=False)
