
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


    def lighten(self):
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
        self.add_cmd_handler('schedule', self.schedule)

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


    def schedule(self, message):
        #print('[core.schedule] message: {0}'.format(message))
        
        ''' This is called, for example when a layer should be
            discharged, to flush all the pending messages to
            lower layers.
        '''
        self.core.dispatch(message['params'])

        return result
