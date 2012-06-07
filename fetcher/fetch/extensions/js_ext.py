# -*- coding: utf-8 -*-

from BeautifulSoup import BeautifulSoup

from base import BaseExtension
from js_aux import HtmlWindow


class JSExtension(BaseExtension):
    @property
    def js(self):
        if not hasattr(self, '_js'):
            self._js = HtmlWindow(
                url=self.response.url,
                dom_or_doc=BeautifulSoup(self.response.content)
            )
        return self._js
