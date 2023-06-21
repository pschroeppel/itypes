#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

from ..json_registry import RegistryPath
from .visualizations.registry import _instantiate_visualization, _reinstantiate_visualization
from ..type import is_list, FormattedFloat, FAIL
from ..utils import align_tabs
from ..grid2d import Grid2D
from copy import deepcopy
from ._node import _DatasetNode
from ..log import log as logger


class _Iterator:
    def __init__(self, met):
        self._met = met
        self._ids = met.ids()
        self._index = 0

    def __next__(self):
        if self._index >= len(self._ids):
            raise StopIteration

        value = self._met[self._ids[self._index]]
        self._index += 1
        return value


class _Metric(_DatasetNode):
    def _str(self, prefix="", indent="  "):
        str = ""
        str += prefix + f"{self.id()+':'}"
        for key, value in self.params().items():
            str += f"\t{key}={value}"
        return str

    def str(self, prefix="", indent="  "):
        return align_tabs(self._str(prefix, indent))

    def __str__(self):
        return self.str()

    def id(self):           return self._path[-1]
    def type(self):         return self._get("type")
    def data(self):         return self._get_var("data")
    def ref(self):          return self._get_var("ref")
    def params(self):       return self._dict()

    def value_var(self):    return self._get_var("value_var", type="float-scalar", create=True)
    def map_var(self):      return self._get_var("map_var", type="float", create=True)

    def set_value(self, value):
        self._set("value", float(value))
        if hasattr(value, 'precision'):
            self._set("precision", value.precision())

    def value(self):
        value = self._get("value")
        precision = self._get("precision", 2)
        return FormattedFloat(value, precision)

    def variable_ids(self):
        ids = []
        data_id = self._get("data")
        if data_id is not None: ids.append(data_id)
        ref_id = self._get("ref")
        if ref_id is not None: ids.append(ref_id)
        value_var_id = self._get("value_var")
        if value_var_id is not None: ids.append(value_var_id)
        map_var_id = self._get("map_var")
        if map_var_id is not None: ids.append(map_var_id)        
        return ids 

    def compute(self, save_result=True, save_values=False, save_maps=False, device=None, log=False):
        return self.update(save_result, save_values, save_maps, device, recompute=True, log=log)

    def update(self, save_result=True, save_values=False, save_maps=False, device=None, recompute=False, log=False):
        import torch
        if device is None:
            device = torch.device("cpu")

        from imetrics import compute_pair_metric, metric_precision

        data_id = self._get("data", FAIL)
        ref_id = self._get("ref", FAIL)
        type = self._get("type", FAIL)

        errors = []
        for item in self._ds: 
            data = item[data_id].data(dims="hwc", device=device)
            ref = item[ref_id].data(dims="hwc", device=device)

            value = None
            if save_values:
                value_var = self.value_var()
                if value_var is not None and (item.group_id(), item.id()) in value_var:
                    value = value_var[item.group_id(), item.id()].data()
            value_ok = value is not None

            map_ok = True
            if save_maps:
                map_var = self.map_var()
                if map_var is not None and (item.group_id(), item.id()) not in map_var:
                    map_ok = False

            if value_ok and map_ok and not recompute:
                if log:
                    logger.info(f"{self.id()} for {item.group_id()}/{item.id()}: {value}")
                errors.append(value)
                continue

            result = compute_pair_metric(type,
                data=data,
                ref=ref,
                dims="hwc",
                device=device,
                compute_map=save_maps
            )

            if save_values:
                value_var = self.value_var()
                if value_var is None:
                    raise Exception(f"_Metric is missing \"value_var\" parameter")
                value_var[item.group_id(), item.id()].set_data(float(result.error()))

            if save_maps: 
                map_var = self.map_var()
                if map_var is None:
                    raise Exception(f"_Metric is missing \"map_var\" parameter")
                map_var[item.group_id(), item.id()].set_data(result.map(dims="hwc"))

            if log:
                logger.info(f"{self.id()} for {item.group_id()}/{item.id()}: {result.error()}")

            errors.append(result.error())

        mean_error = FormattedFloat(
            sum(errors) / len(errors),
            metric_precision(self.type())
        )

        if log:
            logger.confirm(f"{self.id()} total: {mean_error}")

        if save_result:
            self.set_value(mean_error)
            self._ds._do_auto_write()

        return mean_error

    def change_vars(self, mapping):
        data_id = self._get("data")
        if data_id in mapping:
            self._set("data", mapping[data_id])
        ref_id = self._get("ref")
        if ref_id in mapping:
            self._set("ref", mapping[ref_id])
        value_var_id = self._get("value_var")
        if value_var_id in mapping:
            self._set("value_var", mapping[value_var_id])
        map_var_id = self._get("map_var")
        if map_var_id in mapping:
            self._set("map_var", mapping[map_var_id])


class _Metrics(_DatasetNode):
    def __init__(self, ds):
        super().__init__(ds, RegistryPath("metrics"))

    def create(self, type, id, data, ref, **kwargs):
        path = self._path + id
        if path in self._reg:
            self._reg.remove(self._path + id)
        if 'value_var' not in kwargs:
            kwargs['value_var'] = id + ".errors"
        if 'map_var' not in kwargs:
            kwargs['map_var'] = id + ".maps"
        d = {
            "type": type,
            "data": data,
            "ref": ref
        }
        d.update(kwargs)
        self._reg[self._path + id] = d
        return self[id]

    def ids(self):
        return self._keys()

    def __contains__(self, id):
        return self._path + id in self._reg

    def __getitem__(self, id):
        if is_list(id):
            if not self._exists():
                raise Exception(f"metric \"{id}\" not found")
            for key, value in self._reg[self._path].items():
                if value['index'] == id:
                    return _Metric(
                        self._ds,
                        self._path + key,
                     )
            raise Exception(f"visualization \"{id}\" not found")
        else:
            return _Metric(
                self._ds,
                self._path + id,
            )

    def __delitem__(self, id):
        self.remove(id)
        self._ds._do_auto_write()

    def __iter__(self):
        return _Iterator(self)

    def remove(self, id):
        if is_list(id):
            for key, value in self._reg[self._path].items():
                if value['index'] == id:
                    self._reg.remove(self._path + key)
            raise Exception(f"metric \"{id} not found")
        else:
            self._reg.remove(self._path + id)

    def __str__(self):
        return self.str()

    def str(self, prefix="", indent="  "):
        return align_tabs(self._str(prefix, indent))

    def _str(self, prefix="", indent="  "):
        str = ""
        for met in self:
            str += met._str(prefix, indent) + "\n"
        return str

    def __setitem__(self, id, met):
        params = met.params()
        self.create(**params, id=id)

    def copy_from(self, other):
        for other_met in other:
            self.create(**other_met.params(), id=other_met.id())


    def verify(self, log=True):
        succeeded = True
        for met in self:
            if log:
                logger.info(f"Checking metric {met.id()}")
            for var_id in met.variable_ids():
                if var_id not in self._ds.var:
                    succeeded = False
                    if log:
                        logger.error(f"Metric {met.id()} references non-existent variable {var_id}")

        return succeeded

    def sanitize(self, log=True):
        remove_list = []
        for met in self:
            if log:
                logger.info(f"Checking metric {met.id()}")
            for var_id in met.variable_ids():
                if var_id not in self._ds.var:
                    remove_list.append(met.id())
                    if log:
                        logger.warning(
                            f"Removing metric {met.id()} as it references non-existent variable {var_id}")

        for id in remove_list:
            del self[id]

        return True
