# -*- coding: utf-8 -*-

class FetcherException(Exception): pass

class XPathNotFound(FetcherException): pass
class FormsException(FetcherException): pass

class TimeoutError(FetcherException): pass
class ConnectionError(FetcherException): pass
class AuthError(FetcherException): pass
class NetworkError(FetcherException): pass
