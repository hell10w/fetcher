# -*- coding: utf-8 -*-

from forms_ext import FormsExtension
from lxml_ext import LXMLExtension, Structure
from js_ext import JSExtension


class Extensions(LXMLExtension, FormsExtension, JSExtension):
    pass
