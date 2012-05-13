from time import sleep

import pycurl


class MultiCurl:
    def __init__(self, threads_count=20):
        self.threads_count = threads_count
        self.index = 0
        self.tasks = ['http://localhost' for _ in xrange(1000)]
        self.multi_handle = pycurl.CurlMulti()
        self.multi_handle.handles = [pycurl.Curl() for _ in xrange(threads_count)]
        self.curls_pool = self.multi_handle.handles[:]

    def __del__(self):
        # Cleanup
        for curl in self.multi_handle.handles:
            curl.close()
        self.multi_handle.close()

    def add_task(self):
        '''If there is an url to process and a free curl object, add to multi stack'''
        url = self.tasks.pop()
        curl = self.curls_pool.pop()
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.WRITEFUNCTION, lambda chunk: None)
        curl.index = self.index
        self.index += 1
        self.multi_handle.add_handle(curl)

    def main_loop(self):
        # Main loop
        while True:
            if not self.tasks and self.is_empty(): #len(self.curls_pool) < self.threads_count:
                break
            while self.tasks and not self.is_full():
                self.add_task()
            self.wait_available()
            self.process_results()

    def is_full(self):
        return not len(self.curls_pool)

    def is_empty(self):
        return len(self.curls_pool) == self.threads_count

    def process_results(self):
        while True:
            num_q, ok_list, err_list = self.multi_handle.info_read()
            for c in ok_list:
                self.multi_handle.remove_handle(c)
                print "Success:", c.index, c.getinfo(pycurl.EFFECTIVE_URL)
                self.curls_pool.append(c)
            for c, errno, errmsg in err_list:
                self.multi_handle.remove_handle(c)
                print "Failed: ", errno, errmsg
                self.curls_pool.append(c)
            if num_q == 0:
                break
            # Currently no more I/O is pending, could do something in the meantime
        # (display a progress bar, etc.).
        # We just call select() to sleep until some more data is available.
        self.multi_handle.select(1.0)

    def wait_available(self):
        '''Check for curl objects which have terminated, and add them to the freelist'''
        while True:
            ret, num_handles = self.multi_handle.perform()
            if ret != pycurl.E_CALL_MULTI_PERFORM:
                break

worker = MultiCurl()
worker.main_loop()
