# -*- coding: utf-8 -*-


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
