
import queue
from multiprocessing import Queue
from threading import Thread

from units.unit import Unit


class MessageMgr:

    def __init__(self, core):
        super(MessageMgr, self).__init__(core)
        self._messages = Queue()
        self._thread = None
        self._halt = False

    ''' 
    '''
    def handler(self):
        while not self._halt:
            message = self.pop()
            print('[i] Message Manager - New message: {0}'.format(message))
            if message['dst'] == self.core.name:
                self.core.digest(message)
            else:
                self.core.forward(message)

    def start(self):
        self.handler()

    def halt(self):
        self._halt = True

    def push(self, message):
        self._messages.put(message)

    def pop(self):
        message = None
        while not message:
            try:
                message = self._messages.get(timeout=1)
            except queue.Empty:
                if self._halt:
                    break
                continue
        return message