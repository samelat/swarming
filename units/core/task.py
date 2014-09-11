
import queue
from multiprocessing import Process

from units.modules.unit import Unit
from units.modules.messenger import Messenger


class Task(Unit):

    name = 'task'

    def __init__(self, core, unit, task_id):
        super(Task, self).__init__(core)
        self._messenger = Messenger(self)
        self._sync_msgs = queue.Queue()

        self._unit = unit
        self._process = None
        self.tid = task_id

    def _handler(self):
        while not self.halt:
            try:
                message = self._sync_msgs.get(timeout=1)
            except queue.Empty:
                continue
            self._unit.dispatch(message)

    def _launcher(self):
        print('[{0}] starting ...'.format(self.unit_id()))
        self._unit.tid = self.tid
        self._messenger.start()
        self._handler()

    def start(self):
        self._process = Process(target=self._launcher)
        self._process.start()

    def forward(self, message):
        if message['dst'] == self._unit.unit_id():
            if ('async' in message) and not message['async']:
                self._sync_msgs.push(message)
            else:
                self._unit.digest(message)
        else:
            super(Task, self).forward(message)

    def dispatch(self, message):
        self._messenger.push(message)

    ''' ############################################
        Command Handlers
    '''
    def halt(self, message):
        self.halt = True
        self._messenger.halt()
