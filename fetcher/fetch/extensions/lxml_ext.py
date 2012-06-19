# -*- coding: utf-8 -*-

from lxml.etree import fromstring as base_fromstring
from lxml.html import fromstring as html_fromstring

from base import BaseExtension
from lxml_aux import TreeInterface, Structure, Chunk, DotDict


class LXMLExtension(BaseExtension):
    @property
    def html(self):
        if not hasattr(self, '_html'):
            self._html = TreeInterface(
                html_fromstring(
                    self.response.content.encode(self.response.charset or 'utf-8'),
                    base_url=self.response.url
                )
            )
        return self._html

    @property
    def xml(self):
        if not hasattr(self, '_xml'):
            self._xml = TreeInterface(
                base_fromstring(
                    self.response.raw_content,
                    base_url=self.response.url
                )
            )
        return self._xml
