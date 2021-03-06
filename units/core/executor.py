
import queue
import logging
from multiprocessing import Process

from modules.unit import Unit
from modules.message import Message
from modules.messenger import Messenger


class Executor(Unit):

    name = 'executor'

    def __init__(self, core, layer):
        super(Executor, self).__init__(core)
        self.logger = logging.getLogger(__name__)
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

            except KeyboardInterrupt:
                self.halt = True
                continue
            #print('[executor.async] new message: {0}'.format(message))

            result = self.core.dispatch(message)

            if result['status'] <= 0:
                response = Message(message).make_response(result)
                if response:
                    self.core.dispatch(response)
        self._messenger.stop()


    def _launcher(self):
        self.logger.info('Starting Executor ...')

        self.core.layer = self.layer
        self.core.clean()

        self._sync_msgs = queue.Queue()
        self._messenger.start()
        self._handler()
        self._messenger.stop()


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
        return self._messenger.push(message)


    ''' ############################################
        Command Handlers
    '''
    def stop(self, message=None):
        # If the method is called by a message...
        if message:
            self.halt = True
            return {'status':0}

        else:
            msg = {'dst':'executor', 'src':'core', 'cmd':'stop', 'layer':self.layer, 'params':{}}
            self.dispatch(msg)
            self._process.join()
