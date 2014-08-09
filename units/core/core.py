
from units.unit import Unit
from units.core.task_mgr import TaskMgr
from units.core.message_mgr import MessageMgr

from units.http import HTTP
from units.event_mgr import EventMgr
from units.json_iface import JSONIface
from units.dictionary_mgr import DictionaryMgr


class Core(Unit):

    def __init__(self):
        super(Core, self).__init__()
        self._task_mgr    = TaskMgr(self)
        self._message_mgr = MessageMgr(self)

        ''' TODO: It is better if we take the list of
            modules to load from a config file or something
            like that (do not hardcode them).
        '''
        self.modules = {}
        self.modules[JSONIface.name] = JSONIface(self)
        self.modules[HTTP.name] = HTTP(self)

    def _sync_halt(self, message):
        print('[i] Waiting for the service...')
        for module in self.modules.values():
            module.halt()

        self._message_mgr.halt()

    ''' 
    '''
    def dispatch(self, message):
        self._message_mgr.push(message)

    def start(self):
        
        self.sync_commands['halt'] = self._sync_halt

        print('[i] Starting all standard modules...')
        for module in self.modules.values():
            module.start()

        self._task_mgr.start()
        self._message_mgr.start()
