
import queue
from multiprocessing import Process

from modules.unit import Unit
from modules.message import Message
from modules.messenger import Messenger


class Executor(Unit):

    name = 'executor'

    def __init__(self, core, layer):
        super(Executor, self).__init__(core)
        self.layer = layer
        self._messenger = Messenger(self)

        self._sync_msgs = None
        self._process = None


    def _handler(self):
        while not self.halt:
            try:
                message = self._sync_msgs.get(timeout=1)
            except queue.Empty:
                continue
            #print('[executor.async] new message: {0}'.format(message))
            result = self.core.dispatch(message)

            if result['status'] <= 0:
                response = Message(message).make_response(result)
                if response:
                    self.core.dispatch(response)


    def _launcher(self):
        #print('[executor] starting executor {0}...'.format(self.layer))
        self.core.layer = self.layer
        self.core.clean()

        self._sync_msgs = queue.Queue()
        self._messenger.start()

        self._handler()


    @classmethod
    def build(cls, core):
        if core.layer == 0:
            lid = len(core.executors) + 1
            core.executors[lid] = Executor(core, lid)
            core.executors[lid].start()
            return {'status':0}
        return {'status':-1}


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
        #print('[{0}.dispatch] {1}'.format(self.name, Message(message)))
        return self._messenger.push(message)


    ''' ############################################
        Command Handlers
    '''
    def halt(self, message):
        self.halt = True
        self._messenger.halt()

        return {'status':0}
