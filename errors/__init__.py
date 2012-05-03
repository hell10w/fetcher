# -*- coding: utf-8 -*-

class FetcherException(Exception): pass
class TaskParametersError(FetcherException): pass
class UnknownMethod(FetcherException): pass