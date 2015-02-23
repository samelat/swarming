
from threading import Lock
from multiprocessing import Process

from units.tasker.orm import ORM
from units.modules.unit import Unit
from units.modules.messenger import Messenger

from units.tasker.logic import Logic
from units.tasker.knowledge import Knowledge


class Tasker(Unit):

    name = 'tasker'

    def __init__(self, core):
        super(Tasker, self).__init__(core)
        self._messenger = Messenger(self)

        lock = Lock()
        self.knowledge = None
        self.logic = None
        self.uiapi = None

    ''' ############################################

    '''
    def start(self):
        print('[tasker] Starting')
        self.knowledge = Knowledge(self, ORM(lock))
        self.logic = Logic(self, ORM(lock))
        self.uiapi = None

        self.add_cmd_handler('get', self.knowledge.get)
        self.add_cmd_handler('set', self.knowledge.set)

        self._messenger.start()

    def dispatch(self, message):
        result = self._messenger.push(message)
        return result

    ''' ############################################
        Command Handlers
    '''
    def halt(self, message):
        self.halt = True
        self._messenger.halt()
