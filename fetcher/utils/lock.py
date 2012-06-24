# -*- coding: utf-8 -*-

from fcntl import flock, LOCK_EX, LOCK_NB


fh = None


def is_single_instance(lockname):
    '''Проверка наличия запущенных копий скрипта'''
    global fh
    fh = open(lockname, 'w')
    try:
        flock(fh.fileno(), LOCK_EX | LOCK_NB)
    except:
        return False
    return True
