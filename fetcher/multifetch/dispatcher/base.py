# -*- coding: utf-8 -*-


class BaseDispatcher(object):
    def __init__(self, **kwargs):
        super(BaseDispatcher, self).__init__()

    def process_task(self, task):
        '''Стартует асинхронное выполнение задачи'''
        pass

    def is_empty(self):
        '''Проверяет пустоту пула выполняемых задач'''
        return True

    def is_full(self):
        '''Проверяет заполненность пула выполняемых задач'''
        return False

    def wait_available(self):
        '''Проверяет выполненность задач в пуле'''
        pass

    def finished_tasks(self):
        '''Генератор выполненных задач'''
        pass
