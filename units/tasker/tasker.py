
from threading import Lock
from multiprocessing import Process

from units.tasker.orm import ORM
from units.modules import tools
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
        self.knowledge = Knowledge(self, ORM(lock))
        self.logic = Logic(self, ORM(lock))

    ''' ############################################

    '''
    def start(self):
        print('[brain] Starting')
        self.add_cmd_handler('get', self.knowledge.get)
        self.add_cmd_handler('set', self.knowledge.set)
        self._messenger.start()

    def dispatch(self, message):
        print('[tasker] dispatching')
        result = self._messenger.push(message)
        print('[tasker] dispatch result: {0}'.format(result))
        return result

    ''' ############################################
        Command Handlers
    '''
    def halt(self, message):
        self.halt = True
        self._messenger.halt()
