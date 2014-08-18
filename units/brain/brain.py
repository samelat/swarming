
from multiprocessing import Process

from units.modules import tools
from units.modules.unit import Unit
from units.modules.messenger import Messenger

from units.brain.knowledge import Knowledge


class Brain(Unit):

    name = 'brain'

    def __init__(self, core):
        super(Brain, self).__init__(core)
        self._messenger = Messenger(self)
        self._knowledge = Knowledge(self)

    ''' ############################################
        Command Handlers
    '''
    def halt(self, message):
        self._messenger.halt()

    ''' ############################################

    '''
    def start(self):
        self.add_cmd_handler('add_subunit', self._knowledge.add_subunit)
        self._messenger.start(True)

    def dispatch(self, message):
        self._messenger.push(message)