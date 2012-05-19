# -*- coding: utf-8 -*-

from forms_ext import FormsExtension
from lxml_ext import LXMLExtension
from js_ext import JSExtension


class Extensions(LXMLExtension, FormsExtension, JSExtension):
    pass
