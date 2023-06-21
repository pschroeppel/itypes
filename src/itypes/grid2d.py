#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

from .type import is_list

class Grid2D:
    def __init__(self, none_in_range=False, none_outside_range=False):
        self._items = {}
        self._min_col = None 
        self._max_col = None 
        self._min_row = None 
        self._max_row = None
        self._none_in_range = none_in_range
        self._none_outside_range = none_outside_range

    def __setitem__(self, key, value):
        if not is_list(key):
            raise KeyError("Key needs to be two-dimensional")

        col, row = key
        if self._min_row is None or row < self._min_row: self._min_row = row
        if self._max_row is None or row > self._max_row: self._max_row = row
        if self._min_col is None or col < self._min_col: self._min_col = col
        if self._max_col is None or col > self._max_col: self._max_col = col

        self._items[key] = value

    def __getitem__(self, key):
        if not is_list(key):
            raise KeyError("Key needs to be two-dimensional")

        col, row = key

        if col > self._max_col or col < self._min_col or row > self._max_row or row < self._min_row:
            if self._none_outside_range:
                return None
            else:
                raise KeyError(key)

        if key not in self._items:
            if self._none_in_range:
                return None
            else:
                raise KeyError(key)

        return self._items[key]

    def __delitem__(self, key):
        if not is_list(key):
            raise KeyError("Key needs to be two-dimensional")

        del self._items[key]

        self._min_col = None
        self._max_col = None
        self._min_row = None
        self._max_row = None

        for pos in self._items.keys():
            col, row = pos
            if self._min_row is None or row < self._min_row: self._min_row = row
            if self._max_row is None or row > self._max_row: self._max_row = row
            if self._min_col is None or col < self._min_col: self._min_col = col
            if self._max_col is None or col > self._max_col: self._max_col = col

    def __contains__(self, item):
        return item in self.keys()

    def remove_values(self, value):
        positions = []
        for pos, item_value in self._items.items():
            if item_value == value:
                positions.append(pos)

        for pos in positions:
            del self[pos]

    def set(self, col, row, value):
        self[col, row] = value

    def get(self, col, row):
        return self[col, row]

    def row_range(self):
        if len(self._items) == 0: 
            return [] 
        return range(self._min_row, self._max_row + 1)

    def col_range(self):
        if len(self._items) == 0: 
            return [] 
        return range(self._min_col, self._max_col + 1)

    def items(self):
        return self._items.items()

    def keys(self):
        return self._items.keys()

    def values(self):
        return self._items.values()

    def min_col(self):
        return self._min_col
        
    def max_col(self):
        return self._max_col

    def num_cols(self):
        if len(self._items) == 0: return 0 
        return self._max_col - self._min_col + 1

    def min_row(self):
        return self._min_row

    def max_row(self):
        return self._max_row

    def num_rows(self):
        if len(self._items) == 0: return 0
        return self._max_row - self._min_row + 1
