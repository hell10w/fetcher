# -*- coding: utf-8 -*-

from lxml.html import fromstring as html_fromstring, tostring as html_tostring
from lxml.etree import fromstring as xml_fromstring

from fetcher.errors import XPathNotFound
from fetcher.fetch.temporaryfile import TempFile
from base import BaseExtension


class DotDict(dict):
    def __getattr__(self, item):
        return self[item]


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
            body = self.response.get_body()
            if not body:
                body = '<html></html>'
            self._html_tree = html_fromstring(body)
        return self._html_tree

    @property
    def xml_tree(self):
        if not hasattr(self, '_xml_tree'):
            body = self.response.get_unicode_body()
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
                    if isinstance(value, Structure):
                        item[key] = parser(element, value)
                    else:
                        res = element.xpath(value)
                        if res:
                            item[key] = res[0].strip()
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

    def save_html_content(self):
        temp_file = TempFile(delete_on_finish=False)
        temp_file.write(self.html_content())
        return temp_file
