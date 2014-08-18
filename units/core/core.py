
from units.modules.unit import Unit
from units.modules.messenger import Messenger

from units.http import HTTP
from units.brain.brain import Brain
from units.webui.webui import WebUI

from units.core.scheduler import Scheduler
from units.core.event_mgr import EventMgr


class Core(Unit):

    name = 'core'

    def __init__(self):
        super(Core, self).__init__()
        self._scheduler = Scheduler(self)
        self._messenger = Messenger(self)
        self._event_mgr = EventMgr(self)

        ''' TODO: It is better if we take the list of
            modules to load from a config file or something
            like that (do not hardcode them).
        '''
        self.units = {}
        self.units[WebUI.name] = WebUI(self)
        self.units[HTTP.name]   = HTTP(self)
        self.units[Brain.name]  = Brain(self)

    ''' ############################################
        Core Unit Commands
        ############################################
    '''
    def halt(self, message):
        print('[core] Broadcasting "halt" message...')
        for unit_name, unit in self.units.items():
            cmsg = message.copy()
            cmsg['dst'] = unit_name
            print('[core] Sending from "halt" message: {0}'.format(cmsg))
            unit.dispatch(cmsg)
            unit.wait()
        print('[core] Halting Message Manager...')
        self._messenger.halt()
        self._scheduler.halt()

    ''' ############################################
    '''
    def forward(self, message):
        print('[core] Forwarding message to {0}'.format(message['dst']))
        if message['dst'] in self.units:
            self.units[message['dst']].dispatch(message)
        # TODO: We could generate a error here, informing that
        #       the dst module does not exist.

    def dispatch(self, message):
        self._messenger.push(message)

    ''' ############################################
    '''
    def start(self):
        print('[core] Starting all standard units...')
        for unit in self.units.values():
            unit.start()

        self._scheduler.start()
        self._messenger.start()
