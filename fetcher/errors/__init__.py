# -*- coding: utf-8 -*-

class FetcherException(Exception): pass

class TimeoutError(FetcherException): pass
class ConnectionError(FetcherException): pass
class AuthError(FetcherException): pass
class NetworkError(FetcherException): pass
