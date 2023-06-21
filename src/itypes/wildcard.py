#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

from .type import is_list
from fnmatch import fnmatch


def wildcard_match(haystack, needles, extra=None):
    needle_pairs = []
    needle_parts = needles.split(',') if not is_list(needles) else needles
    for needle in needle_parts:
        if extra and extra in needle: needle_pairs.append(needle.split(extra))
        else:                         needle_pairs.append((needle, None))

    result = []
    for (needle, suffix) in needle_pairs:
        if suffix:
            if is_list(haystack):
                result += [ent + extra + suffix for ent in haystack if fnmatch(ent, needle)]
            else:
                result += [ent + extra + suffix for ent in fnmatch(haystack, needle)]
        else:
            if is_list(haystack):
                result += [ent for ent in haystack if fnmatch(ent, needle)]
            else:
                result += [fnmatch(haystack, needle)]
    return result
