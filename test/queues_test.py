# -*- coding: utf-8 -*-

from random import shuffle
from unittest import TestCase, main

from tasks.queues import get_tasks_queue
from tasks import Task


class Test(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tasks = get_tasks_queue()

    @classmethod
    def setDownClass(cls):
        pass

    def test_queue(self):
        '''Проверка работы очереди'''

        count = 10
        numbers = range(count)

        shuffle(numbers)

        while numbers:
            number = numbers.pop()
            self.tasks.put((number, number))

        while not self.tasks.empty():
            numbers.append(self.tasks.get()[1])

        self.assertListEqual(numbers, range(count))

    def test_tasks(self):
        '''Проверка работы с задачами'''

        count = 10
        options = {
            'dsfsdf': 'sdfsdf',
            'dsfewewe': 'sdfsdxx'
        }

        tasks = [Task(index=index, **options) for index in range(count)]

        shuffle(tasks)

        for task in tasks:
            self.tasks.put((task.index, task))

        indexes = []

        while not self.tasks.empty():
            _, task = self.tasks.get()
            indexes.append(task.index)

        self.assertListEqual(indexes, range(count))


if __name__ == "__main__":
    main()
