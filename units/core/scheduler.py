
from threading import Queue
from threading import Condition

class Scheduler:

    def __init__(self, core):
    	self._core = core
        self._messages = Queue()
        self._halt = False

        self._processes = []

    ''' 
    '''
    def _handler(self):
        while True:
            message = self.pop()
            if not message:
                break
            print('[core] Scheduler - New message: {0}'.format(message))

    def push(self, message):
        self._messages.put(message)

    def pop(self):
        message = None
        while not (message or self._halt):
            try:
                message = self._messages.get(timeout=1)
            except queue.Empty:
                continue
        return message

    def halt(self):
    	self._halt = True

    def start(self):
    	self._handler();

    def schedule(self, message):
        print('[core] Scheduling: {0}'.format(message))