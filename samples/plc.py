from time import time

import pylibcurl
import pycurl


def worker(function, repeat=100):
    elapsed = 0
    for _ in range(repeat):
        start = time()
        function()
        elapsed += time() - start
    print
    print elapsed / repeat
    print


def pylibcurl_test():
    multi = pylibcurl.Multi()
    for _ in xrange(10):
        curl = pylibcurl.Curl(
            url='http://localhost',
            writefunction=lambda chunk: None
        )
        multi.add_handle(curl)
    multi.perform()


def pycurl_test():
    multi = pycurl.CurlMulti()
    multi.handles = []
    for _ in xrange(10):
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, 'http://localhost')
        curl.setopt(pycurl.WRITEFUNCTION, lambda chunk: None)
        multi.add_handle(curl)
        multi.handles.append(curl)
    multi.perform()


if __name__ == '__main__':
    worker(pylibcurl_test)
    worker(pycurl_test)
