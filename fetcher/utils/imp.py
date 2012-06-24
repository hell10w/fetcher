# -*- coding: utf-8 -*-

import sys


def import_module(name):
    __import__(name)
    return sys.modules[name]
