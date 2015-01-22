
import random

from units.http import HTTP
from units.webui.webui import WebUI
from units.modules.unit import Unit
from units.tasker.tasker import Tasker
from units.core.executor import Executor

from units.modules import tools


class Core(Unit):

    name = 'core'
    layers = 3

    def __init__(self):
        super(Core, self).__init__()
        self._executors = {}
        self._units = {}
        self.layer = 0

    def add_unit(self, unit):
        if unit.name not in self._units:
            self._units[unit.name] = unit
            if unit.light:
                unit.start()

    ''' ############################################
    '''
    def start(self):
        self.add_cmd_handler('schedule', self.schedule)

        ''' TODO: It is better if we take the list of
            modules to load from a config file or something
            like that (do not hardcode them).
        '''
        ''' We have to follow this order in the units' declaration and 
            starting because in another way they will not exist in the
            different layers.
        '''
        # HEAVY UNITS
        self.add_unit(Tasker(self))
        self.add_unit(WebUI(self))

        # LIGHT UNITS
        self.add_unit(HTTP(self))

        # NEW LAYERS (EXECUTORS)
        for lid in range(0, self.layers):
            self._executors[lid] = Executor(self, lid)
            self._executors[lid].start()

        self._units[WebUI.name].start()
        self._units[Tasker.name].start()

    ''' ############################################
    '''
    def forward(self, message):
        print('[core] Forwarding [{0}]--------({1})-------->[{2}]'.format(message['src'], self.layer, message['dst']))
        ''' This condition is for cases where one unit send
            a message to another one in the same layer.
        '''
        if not 'layer' in message:
            message['layer'] = self.layer

        if message['layer'] == self.layer:
            if message['src'] in self._units:
                self._executors[self.layer].dispatch(message)
            else:
                self._units[message['dst']].dispatch(message)
        else:
            self._executors[message['layer']].dispatch(message)


    ''' ############################################
        Core Unit Commands
        ############################################
    '''
    def halt(self, message):
        print('[core:{0}] Halting Layer ...'.format(self.layer))
        
    def schedule(self, message):
        print('[core.schedule] message: {0}'.format(tools.msg_to_str(message)))
        params = message['params']
        
        ''' This is called, for example when a layer should be
            discharged, to flush all the pending messages to
            the layer 0.
        '''
        if 'layer' in params:
            try:
                layer = params['layer']
                for msg in params['messages']:
                    msg['layer'] = layer
                    self._executors[layer].dispatch(msg)
            except KeyError:
                return {'error':'-1', 'msg':'Layer {0} does not exist'.format(layer)}
        else:
            ''' If we have to schedule messages from a leyer 
                higher than 0, we forward the schedule message to
                the layer 0 to make the layer digest it.
            '''
            if self.layer:
                self._executors[0].dispatch(message)
            else:
                for msg in params['messages']:
                    if (not 'layer' in msg) or (msg['layer' >= self.layers]):
                        msg['layer'] = random.randint(0, self.layers - 1)
                    self._executors[msg['layer']].dispatch(msg)

        return {'state':'done'}
