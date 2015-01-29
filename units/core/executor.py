
import queue
from multiprocessing import Process

from units.modules.unit import Unit
from units.modules.message import Message
from units.modules.messenger import Messenger


class Executor(Unit):

    name = 'executor'

    def __init__(self, core, layer):
        super(Executor, self).__init__(core)
        self.layer = layer
        self._messenger = Messenger(self)
        self._sync_msgs = queue.Queue()

        self._process = None

    def _handler(self):
        while not self.halt:
            try:
                message = self._sync_msgs.get(timeout=1)
            except queue.Empty:
                continue
            print('[executor.async] new message: {0}'.format(Message(message)))
            result = self.core.dispatch(message)

            if result['status'] <= 0:
                response = Message(message).make_response(result)
                if response:
                    self.core.dispatch(response)


    def _launcher(self):
        print('[executor] starting executor {0}...'.format(self.layer))
        self.core.layer = self.layer
        self._messenger.start()
        self._handler()

    def start(self):
        self._process = Process(target=self._launcher)
        self._process.start()

    def forward(self, message):
        if ('async' in message) and not message['async']:
            self._sync_msgs.put(message)
            return {'status':1, 'channel':message['channel']}
        else:
            return self.core.dispatch(message)

    def dispatch(self, message):
        return self._messenger.push(message)

    ''' ############################################
        Command Handlers
    '''
    def halt(self, message):
        self.halt = True
        self._messenger.halt()

        return {'status':0}
