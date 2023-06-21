#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

from .io import read
from multiprocessing.dummy import Pool as ThreadPool

def read_parallel(urls, num_threads=64, **kwargs):
    def read_with_args(url):
        return read(url, **kwargs)

    pool = ThreadPool(num_threads)
    result = pool.map(read_with_args, urls)
    return result

