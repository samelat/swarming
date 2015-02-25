
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
            print('[{0}.messenger.handler] new message: {1}'.format(self._owner.name, Message(message)))
            if message['dst'] == self._owner.name:
                result = self._owner.digest(message)
            else:
                result = self._owner.forward(message)
            
            if result['status'] <= 0:
                response = Message(message).make_response(result)
                print('[messenger] dispatching response message {0}'.format(message))
                print('[messenger] dispatching response {0}'.format(response))
                if response:
                    self._owner.core.dispatch(response)


    def start(self):
        #print('[{0}.messenger] starting'.format(self._owner.name))
        self._thread = Thread(target=self._handler)
        self._thread.start()

    def halt(self):
        self._halt = True

    def push(self, message):
        print('[{0}.messenger.push] {1}'.format(self._owner.name, Message(message)))
        try:
            _message = Message(message)
        except ValueError:
            return {'status':-1, 'error':'message format error'}

        _message.add_channel()
        self._messages.put(_message.raw)

        return {'status':1, 'channel':_message.raw['channel']}
