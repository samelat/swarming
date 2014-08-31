
from units.modules.unit import Unit
from units.modules.messenger import Messenger

from units.http import HTTP
from units.brain.brain import Brain
from units.webui.webui import WebUI

from units.core.scheduler import Scheduler
from units.core.event_mgr import EventMgr


class Core(Unit):

    uname = 'core'

    def __init__(self):
        super(Core, self).__init__()
        self._scheduler = Scheduler(self)
        self._messenger = Messenger(self)
        # self._event_mgr = EventMgr(self)

        ''' TODO: It is better if we take the list of
            modules to load from a config file or something
            like that (do not hardcode them).
        '''
        self._scheduler.add_unit(WebUI(self))
        self._scheduler.add_unit(HTTP(self))
        self._scheduler.add_unit(Brain(self))

    ''' ############################################
    '''
    def start(self):
        # self.add_cmd_handler('schedule', self._scheduler.schedule)

        self._messenger.start()
        self._scheduler.start()

    ''' ############################################
    '''
    def forward(self, message):
        print('[core] Forwarding message to {0}'.format(message['dst']))
        self._scheduler.forward(message)

    def dispatch(self, message):
        self._messenger.push(message)

    ''' ############################################
        Core Unit Commands
        ############################################
    '''
    def halt(self, message):
        print('[core] Halting Message Manager...')
        self._messenger.halt()
        self._scheduler.halt()
        
