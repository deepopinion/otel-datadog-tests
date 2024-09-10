import gevent.monkey


gevent.monkey.patch_all(thread=True)
