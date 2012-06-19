# -*- coding: utf-8 -*-

from structures import Structure, Chunk, DotDict


class TreeInterface(object):
    def __init__(self, tree):
        self._tree = tree

    @property
    def tree(self):
        return self._tree

    def xpath(self, path, default=None, all=False):
        '''Возвращает первый элемент по заданному xpath'''
        items = self.tree.xpath(path)
        if all:
            return items
        try:
            return items[0]
        except IndexError:
            return default

    def xpath_exists(self, path):
        '''Проверяет наличие xpath на страницу'''
        return len(self.tree.xpath(path)) > 0

    def make_links_absolute(self):
        '''Добавляет к относительным ссылкам текущий url'''
        self._tree.make_links_absolute()

    def structured_xpath(self, xpath='./', *args, **kwargs):
        '''Функция структурированного парсинга страницы с помощью xpath'''
        def parser(element, structure):
            items = []
            for element in element.xpath(structure._xpath):
                item = DotDict()
                for substructure in structure._args:
                    res = parser(element, substructure)
                    if res:
                        item.update(res[0])
                for key, value in structure._kwargs.iteritems():
                    if isinstance(value, (str, unicode)):
                        chunk = Chunk(value, apply_func=lambda item: unicode(item).strip())
                        item[key] = chunk.prepare_element(element)
                    if isinstance(value, Structure):
                        item[key] = parser(element, value)
                    elif isinstance(value, (list, tuple, set)):
                        chunk = Chunk(*value)
                        item[key] = chunk.prepare_element(element)
                    elif isinstance(value, Chunk):
                        item[key] = value.prepare_element(element)
                    else:
                        TypeError('Unknown type for structured type!')
                items.append(item)
            return items

        if isinstance(xpath, (str, unicode)):
            structure = Structure(xpath, *args, **kwargs)
        elif isinstance(xpath, Structure):
            structure = xpath
        else:
            Exception(u'Передан неизвестный аргумент в функцию структруного парсинга')

        return parser(
            self.tree,
            structure
        )
