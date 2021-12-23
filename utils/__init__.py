import platform
from queue import Queue


@property
def is_windows():
    return platform.system() == 'Windows'


def exception_catcher(method):
    def wrapper(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except Exception as exp:
            self.logger.error(str(exp))

    return wrapper


class QueueWrapper(object):
    def __init__(self, allow_clear=False):
        self.allow_clear = allow_clear
        self.queue = Queue()

    def put(self, item):
        if self.allow_clear and self.queue.full():
            self.queue.queue.clear()
        self.queue.put(item)

    def get(self, wait=True):
        if wait:
            return self.queue.get()
        return self.queue.get_nowait()
