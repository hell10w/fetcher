# -*- coding: utf-8 -*-

from unittest import TestCase, main

from fetcher.fetch.temporaryfile import TempFile


class Test(TestCase):
    def test_tempfile(self):
        '''Проверка работы с временным файлом'''

        content = [
            'firstline',
            'secondline'
        ]

        first_file = TempFile()

        writed = ''
        for line in content:
            writed += line
            first_file.write(line)
            self.assertEqual(writed, first_file.read())

        # хз как генератор проверить
        #self.assertSequenceEqual(iter(writed), first_file.read(size=1))


if __name__ == "__main__":
    main()
