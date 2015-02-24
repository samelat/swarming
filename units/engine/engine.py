
from threading import Lock
from multiprocessing import Process

from units.engine.orm import ORM
from units.modules.unit import Unit
from units.modules.messenger import Messenger

from units.engine.tasker import Tasker
from units.engine.knowledge import Knowledge


class Engine(Unit):

    name = 'engine'

    def __init__(self, core):
        super(Engine, self).__init__(core)
        self._messenger = Messenger(self)

        self.knowledge = None
        self.tasker = None
        self.uiapi = None


    def minimal(self):
        self.knowledge = None
        self.tasker = None
        self.uiapi = None


    ''' ############################################

    '''
    def start(self):
        print('[engine] Starting')
        lock = Lock()
        self.knowledge = Knowledge(self, ORM(lock))
        self.logic = Tasker(self, ORM(lock))
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
