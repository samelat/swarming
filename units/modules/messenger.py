
import queue
from multiprocessing import Queue
from threading import Thread

from units.modules.unit import Unit
from units.modules.message import Message


class Messenger:

    def __init__(self, owner):
        self._owner = owner
        self._halt = False
        
        self._messages = Queue()
        self._thread = None

    ''' 
    '''
    def _handler(self):
        while not self._halt:
            try:
                message = self._messages.get(timeout=1)
            except queue.Empty:
                continue
            print('[{0}.messenger] message: {1}'.format(self._owner.name, message))
            if message['dst'] == self._owner.name:
                self._owner.digest(message)
            else:
                self._owner.forward(message)

    def start(self):
        print('[messenger.{0}] starting'.format(self._owner.name))
        self._thread = Thread(target=self._handler)
        self._thread.start()

    def halt(self):
        self._halt = True

    def push(self, message):
        try:
            _message = Message(message)
        except ValueError:
            return {'error':-1}

        self._messages.put(_message.raw)

        return {'channel':_message.raw['channel'], 'error':0}
