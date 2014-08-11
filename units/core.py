
from units.unit import Unit
from units.modules.scheduler import Scheduler
from units.modules.messenger import Messenger

from units.http import HTTP
from units.event_mgr import EventMgr
from units.json_iface import JSONIface
from units.dictionary_mgr import DictionaryMgr


class Core(Unit):

    name = 'core'

    def __init__(self):
        super(Core, self).__init__()
        self._scheduler = Scheduler(self)
        self._messenger = Messenger(self)

        ''' TODO: It is better if we take the list of
            modules to load from a config file or something
            like that (do not hardcode them).
        '''
        self.units = {}
        self.units[JSONIface.name] = JSONIface(self)
        self.units[HTTP.name] = HTTP(self)

    ''' ############################################
        Core Unit Commands
        ############################################
    '''
    def _sync_halt(self, message):
        print('[i] Halting units...')
        for unit in self.units.values():
            unit.halt()
        print('[i] Halting Message Manager...')
        self._messenger.halt()
        self._scheduler.halt()

    ''' ############################################
    '''
    def forward(self, message):
        print('[i] Forwarding message to {0}'.format(message['dst']))
        if message['dst'] in self.units:
            self.units[message['dst']].dispatch(message)
        # TODO: We could generate a error here, informing that
        #       the dst module does not exist.

    def dispatch(self, message):
        self._messenger.push(message)

    ''' ############################################
    '''
    def start(self):
        
        self.sync_commands['halt'] = self._sync_halt

        print('[i] Starting all standard units...')
        for unit in self.units.values():
            unit.start()

        self._scheduler.start()
        self._messenger.start()
