
import queue
from threading import Thread
from multiprocessing import Queue

from modules.unit import Unit
from modules.message import Message


class Messenger:

    def __init__(self, owner):
        self._owner = owner
        
        self._messages = Queue()
        self._thread = None

    ''' 
    '''
    def _handler(self):
        while not self._owner.halt:
            try:
                message = self._messages.get(timeout=1)
            except queue.Empty:
                continue

            if message['dst'] == self._owner.name:
                result = self._owner.digest(message)
            else:
                result = self._owner.forward(message)
            
            if result['status'] <= 0:
                response = Message(message).make_response(result)

                if response:
                    self._owner.core.dispatch(response)

    def start(self):
        self._thread = Thread(target=self._handler, name='messenger')
        self._thread.start()

    def stop(self):
        self._thread.join()

    def push(self, message):

        try:
            _message = Message(message)
        except ValueError:
            return {'status':3, 'error':'message format error'}

        _message.add_channel()
        self._messages.put(_message.raw)

        return {'status':1, 'channel':_message.raw['channel']}
