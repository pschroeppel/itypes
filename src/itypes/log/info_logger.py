#!/usr/bin/env python3

### --------------------------------------- ###
### Part of iTypes                          ###
### (C) 2022 Eddy ilg (me@eddy-ilg.net)     ###
### MIT License                             ###
### See https://github.com/eddy-ilg/itypes  ###
### --------------------------------------- ###

import datetime
import termcolor

INFO = "INFO"
NOTICE = "NOTICE"
WARNING = "WARNING"
ERROR = "ERROR"
CONFIRMATION = "CONFIRM"

_colors = {
    INFO: None,
    NOTICE: "cyan",
    WARNING: "yellow",
    ERROR: "red",
    CONFIRMATION: "green"
}

class _InfoLogger:
    def message(self, level, msg):
        time_str = '{0:%Y-%m-%d %H:%M:%S} - '.format(datetime.datetime.now())
        print(time_str, end='')
        termcolor.cprint(f'{level+":":9s} {msg}', _colors[level])

    def info(self, msg):
        self.message(INFO, msg)

    def notice(self, msg):
        self.message(NOTICE, msg)

    def warning(self, msg):
        self.message(WARNING, msg)

    def error(self, msg):
        self.message(ERROR, msg)

    def confirm(self, msg):
        self.message(CONFIRMATION, msg)

log = _InfoLogger()

