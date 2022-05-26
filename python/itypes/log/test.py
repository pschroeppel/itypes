#!/usr/bin/env python3

from .trace_logger import TraceLogger

class _BaseClass:
    def __init__(self):
        # Note: although there is no base class this has to be done here!
        super().__init__()
        self.__log = TraceLogger()
        self.__log.info("constructor")

    def my_method(self):
        self.__log.info("method")

class TraceLoggerTestClass(_BaseClass):
    def __init__(self):
        super().__init__()
        self.__log = TraceLogger()
        self.__log.info("constructor")

    def my_method(self):
        super().my_method()
        self.__log.info("method")
