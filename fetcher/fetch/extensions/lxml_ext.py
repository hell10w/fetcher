# -*- coding: utf-8 -*-

from lxml.html import fromstring as html_fromstring
from lxml.etree import fromstring as xml_fromstring

from fetcher.errors import XPathNotFound
from base import BaseExtension


# TODO: def xpath_text(self, path, default=NULL, filter=None, smart=False, normalize_space=True)
# TODO: def xpath_number(self, path, default=NULL, filter=None, ignore_spaces=False, smart=False)
# TODO: def find_link_rex(self, rex, make_absolute=True)
# TODO: def find_link(self, href_pattern, make_absolute=True)
# TODO: def follow_link(self, anchor=None, href=None)
# TODO: def find_content_blocks(self, min_length=None)


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
            body = self.response.get_body()
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

    def assert_xpath(self, path):
        self.xpath(path)

    def xpath_exists(self, path):
        return len(self.xpath_list(path)) > 0
