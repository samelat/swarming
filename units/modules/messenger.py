
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
            print('[messenger.{0}] message: {1}'.format(self._owner.name, Message(message)))
            if message['dst'] == self._owner.name:
                result = self._owner.digest(message)
            else:
                ''' TODO:
                    El forward puede tener dos resultados: Uno, el resultado de la ejecucion del
                    comando y otro el resultado de despacharlo. Hay que ver como manejar eso
                '''
                result = self._owner.forward(message)

            response = Message(message).make_response(result)
            if response:
                self._owner.core.dispatch(response)


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
