#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

import sys
import inspect
from itypes import addr

TRACE = -1
DEBUG = 0
INFO = 1
WARNING = 2
ERROR = 3

log_level = INFO

def set_trace_level(level):
    global log_level
    if isinstance(level, str):
        level = str_to_level(level)
    log_level = level

def str_to_level(str):
    if str == "TRACE": return TRACE
    if str == "DEBUG": return DEBUG
    if str == "INFO": return INFO
    if str == "WARNING": return WARNING
    if str == "ERROR": return ERROR
    raise KeyError(str)

def level_to_str(level):
    if level == TRACE: return "TRACE"
    if level == DEBUG: return "DEBUG"
    if level == INFO: return "INFO"
    if level == WARNING: return "WARNING"
    if level == ERROR: return "ERROR"
    return "(unknown)"

class TraceLogger:
    def __init__(self):
        info = inspect.stack()[1]
        self._container = info.frame.f_locals["__class__"]
        self._module_name = self._container.__module__
        self._class_name = self._container.__name__

    def _message(self, level, message):
        global log_level

        if level < log_level:
            return

        info = inspect.stack()[2]
        object = info.frame.f_locals["self"]
        function_name = info.function

        str = ""
        str += f"[{level_to_str(level):>7s}] {self._module_name:40s} {self._class_name:25s} {addr(object):14s} {function_name+'()':30s}: {message}"
        str += "\n"
        sys.stdout.write(str)
        sys.stdout.flush()

    def info(self, msg):
        self._message(INFO, msg)

    def debug(self, msg):
        self._message(DEBUG, msg)

    def trace(self, msg):
        self._message(TRACE, msg)

    def error(self, msg):
        self._message(ERROR, msg)

    def warning(self, msg):
        self._message(WARNING, msg)
