
import queue
from multiprocessing import Process

from units.modules.unit import Unit
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
            print('[executor.async]')
            response = self.core.dispatch(message)


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
            return 
        else:
            return self.core.dispatch(message)

    def dispatch(self, message):
        print('[executor:{0}] dispatching'.format(self.core.layer))
        return self._messenger.push(message)

    ''' ############################################
        Command Handlers
    '''
    def halt(self, message):
        self.halt = True
        self._messenger.halt()
