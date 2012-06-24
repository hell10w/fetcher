# -*- coding: utf-8 -*-

import sys


def import_module(name):
    '''Импорт модуля с именем name'''
    __import__(name)
    return sys.modules[name]
