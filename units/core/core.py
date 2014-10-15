
from units.modules.unit import Unit
from units.modules.messenger import Messenger

from units.http import HTTP
from units.brain.brain import Brain
from units.webui.webui import WebUI

from units.core.scheduler import Scheduler
from units.core.event_mgr import EventMgr


class Core(Unit):

    name = 'core'

    layers = 4

    def __init__(self):
        super(Core, self).__init__()
        self._scheduler = None
        self._executors = {}
        self._units = {}
        # self._event_mgr = EventMgr(self)

    def add_unit(self, unit):
        if unit.name not in self._units:
            self._units[unit.name] = unit
            unit.start()

    ''' ############################################
    '''
    def start(self):
        self.add_cmd_handler('schedule', self._scheduler.schedule)

        ''' TODO: It is better if we take the list of
            modules to load from a config file or something
            like that (do not hardcode them).
        '''
        ''' We have to follow this order in the units' declaration and 
            starting because in another way they will not exist in the
            different layers.
        '''
        # LIGHT UNITS
        self.add_unit(HTTP(self))

        for _lid in range(0, self.layers):
            lid = str(_lid)
            self._executors[lid] = Executor(self._core, lid)
            self._executors[lid].start()

        # HEAVY UNITS
        self.add_unit(Brain(self))
        self.add_unit(WebUI(self))

        self._scheduler = Scheduler(self)
        self._scheduler.start()

    ''' ############################################
    '''
    def forward(self, message):
        print('[core:{0}] Forwarding message to {1}'.format(self.lid, message['dst']))
        uname, lid  = message['dst'].split(':')
        if lid == self.lid:
            self._units[uname].dispatch(message)
        else:
            self._executors[lid].dispatch(message)


    ''' ############################################
        Core Unit Commands
        ############################################
    '''
    def halt(self, params):
        print('[core:{0}] Halting Layer ...'.format(self.lid))
        self._scheduler.halt()
        
