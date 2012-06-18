# -*- coding: utf-8 -*-

from lxml.html import fromstring as html_fromstring, tostring as html_tostring
from lxml.etree import fromstring as xml_fromstring

from fetcher.errors import XPathNotFound
from base import BaseExtension


class DotDict(dict):
    def __getattr__(self, item):
        if hasattr(self, item):
            return self[item]

    def __setattr__(self, key, value):
        self[key] = value


class Chunk(object):
    def __init__(self, xpath, apply_func=None, filter_func=None, one=None):
        self._xpath = xpath
        self._one = one if one is not None else False if filter_func else True
        self._filter_func = filter_func
        self._apply_func = apply_func

    def prepare_element(self, element):
        items = element.xpath(self._xpath)
        if not items:
            return
        if self._one:
            items = items[:1]
        elif self._filter_func:
            items = filter(
                lambda item: self._filter_func(item),
                items
            )
        if self._apply_func and items:
            items = map(
                self._apply_func,
                items
            )
        if items and self._one:
            return items[0]
        else:
            return items


class Structure(object):
    def __init__(self, xpath, *args, **kwargs):
        self._xpath = xpath
        self._args = args
        self._kwargs = kwargs

    def __repr__(self):
        return '<%s %s %s>' % (self._xpath, self._args, self._kwargs)


class LXMLExtension(BaseExtension):
    @property
    def html_tree(self):
        if not hasattr(self, '_html_tree'):
            body = self.response.content
            if not body:
                body = '<html></html>'
            self._html_tree = html_fromstring(body)
        return self._html_tree

    @property
    def xml_tree(self):
        if not hasattr(self, '_xml_tree'):
            body = self.response.content
            if not body:
                body = '<html></html>'
            self._xml_tree = xml_fromstring(body)
        return self._xml_tree

    def xpath(self, path, default=None, filter=None):
        try:
            return self.xpath_list(path, filter)[0]
        except IndexError:
            if default:
                return default
            else:
                raise XPathNotFound('Xpath not found: %s' % path)

    def xpath_list(self, path, filter=None):
        # TODO: что рейзит xpath?
        items = self.html_tree.xpath(path)
        if filter:
            return [x for x in items if filter(x)]
        else:
            return items

    def structured_xpath(self, xpath='./', *args, **kwargs):
        '''Функция структурированного парсинга страницы с помощью xpath'''
        # как пользоваться - смотреть в примере
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
                        chunk = Chunk(value, apply_func=lambda item: item.strip())
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

        if isinstance(xpath, str):
            structure = Structure(xpath, *args, **kwargs)
        elif isinstance(xpath, Structure):
            structure = xpath

        return parser(
            self.html_tree,
            structure
        )

    def assert_xpath(self, path):
        self.xpath(path)

    def xpath_exists(self, path):
        return len(self.xpath_list(path)) > 0

    def make_links_absolute(self):
        self.html_tree.make_links_absolute(self.response.url)

    def html_content(self):
        return html_tostring(self.html_tree, encoding='utf-8')
