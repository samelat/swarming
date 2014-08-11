
import queue
from multiprocessing import Queue
from threading import Thread

from units.unit import Unit


class Messenger:

    def __init__(self, owner):
        self._owner = owner
        self._messages = Queue()
        self._thread = None

        self._halt = False

    ''' 
    '''
    def _handler(self):
        while not self._halt:
            message = self.pop()
            print('[i] ({0}) Message Manager - New message: {1}'.format(self._owner.name, message))
            if message['dst'] == self._owner.name:
                self._owner.digest(message)
            else:
                self._owner.forward(message)

    def start(self, launch=False):
        if launch:
            self._thread = Thread(target=self._handler)
            self._thread.start()
        else:
            self._handler()

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