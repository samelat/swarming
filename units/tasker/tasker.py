
from multiprocessing import Process

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

        self._knowledge = Knowledge(self)
        self.logic = Logic(self)

    ''' ############################################

    '''
    def start(self):
        print('[brain] Starting')
        self.add_cmd_handler('get', self._knowledge.get)
        self.add_cmd_handler('set', self._knowledge.set)
        self._messenger.start()

    def dispatch(self, message):
        self._messenger.push(message)

    ''' ############################################
        Command Handlers
    '''
    def halt(self, message):
        self.halt = True
        self._messenger.halt()
