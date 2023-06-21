#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

from .filesystem import File


itypes_root = File(__file__).path().cd('..').cd('..').abs()
exapmles_root = itypes_root.cd('examples').abs()
data_root = exapmles_root.cd('data').abs()