import gevent
import gevent.pool, gevent.monkey
gevent.monkey.patch_all()
import requests

def worker():
    response = requests.get('http://google.ru/')
    return response.status_code

def worker_finished(result):
    #print result
    pass

pool = gevent.pool.Pool(size=20)

def producer():
    for _ in range(100):
        #gevent.spawn
        print len(pool)
        pool.wait_available()
        #print
        #print pool.free_count()
        #print dir(pool)
        if not pool.full():
            #print '+',
            #pool.spawn(worker)
            pool.apply_async(worker, callback=worker_finished)
        else:
            #print '-',
            pass

        #if pool.free_count() > 0:


        #print '1',
        #print '2',
    pool.join()
    #print 'finished'

#gevent.map_


#pool.wait_available()
#print 'waited'
gevent.spawn(producer).join()
print 'f2'