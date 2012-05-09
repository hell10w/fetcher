#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-
# vi:ts=4:et
# $Id: retriever-multi.py,v 1.29 2005/07/28 11:04:13 mfx Exp $

#
# Usage: python retriever-multi.py <file with URLs to fetch> [<# of
#          concurrent connections>]
#

import sys
import pycurl

# We should ignore SIGPIPE when using pycurl.NOSIGNAL - see
# the libcurl tutorial for more info.
try:
    import signal
    from signal import SIGPIPE, SIG_IGN
    signal.signal(signal.SIGPIPE, signal.SIG_IGN)
except ImportError:
    pass


# Get args
threads_count = 3

urls = ['http://localhost'] * 10

# Make a queue with (url, filename) tuples
tasks = []
for index, url in enumerate(urls):
    tasks.append((url, index))


threads_count = min(threads_count, len(tasks))
print "PycURL %s (compiled against 0x%x)" % (pycurl.version, pycurl.COMPILE_LIBCURL_VERSION_NUM)
print "----- Getting", threads_count, "connections -----"


# Pre-allocate a list of curl objects
multi_handle = pycurl.CurlMulti()
#multi_handle.handles = []
freelist = []
for i in range(threads_count):
    c = pycurl.Curl()
    c.fp = None
    c.setopt(pycurl.FOLLOWLOCATION, 1)
    c.setopt(pycurl.MAXREDIRS, 5)
    c.setopt(pycurl.CONNECTTIMEOUT, 30)
    c.setopt(pycurl.TIMEOUT, 300)
    c.setopt(pycurl.NOSIGNAL, 1)
    #multi_handle.handles.append(c)
    freelist.append(c)


# Main loop
#freelist = multi_handle.handles[:]
num_processed = 0
while num_processed < len(urls):
    # If there is an url to process and a free curl object, add to multi stack
    def fill_tasks():
        while tasks and freelist:
            url, index = tasks.pop(0)
            c = freelist.pop()
            #c.fp = open(filename, "wb")
            c.setopt(pycurl.URL, url)
            #c.setopt(pycurl.WRITEDATA, c.fp)
            c.setopt(pycurl.WRITEFUNCTION, lambda chunk: None)
            multi_handle.add_handle(c)
            # store some info
            c.url = url
            c.____index = index
            # Run the internal curl state machine for the multi stack
    fill_tasks()

    def wait_():
        while 1:
            ret, num_handles = multi_handle.perform()
            if ret != pycurl.E_CALL_MULTI_PERFORM:
                break
            # Check for curl objects which have terminated, and add them to the freelist
    wait_()

    def process_results():
        num_processed = 0
        while 1:
            num_q, ok_list, err_list = multi_handle.info_read()
            for c in ok_list:
                multi_handle.remove_handle(c)
                print "Success:", c.____index, c.url, c.getinfo(pycurl.EFFECTIVE_URL)
                freelist.append(c)
            for c, errno, errmsg in err_list:
                multi_handle.remove_handle(c)
                print "Failed: ", c.url, errno, errmsg
                freelist.append(c)
            num_processed = num_processed + len(ok_list) + len(err_list)
            if num_q == 0:
                break
            # Currently no more I/O is pending, could do something in the meantime
        return num_processed
    num_processed += process_results()

    # (display a progress bar, etc.).
    # We just call select() to sleep until some more data is available.
    multi_handle.select(1.0)


# Cleanup
#for c in multi_handle.handles:
#    c.close()
multi_handle.close()
