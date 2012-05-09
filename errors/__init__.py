# -*- coding: utf-8 -*-

class FetcherException(Exception): pass
class UnknownFetcherTransport(FetcherException): pass
class UnknownFetcherDispatcher(FetcherException): pass