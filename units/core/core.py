
import random

from units.http.http import HTTP
from units.webui.webui import WebUI
from units.modules.unit import Unit
from units.tasker.tasker import Tasker
from units.core.executor import Executor

from units.modules.message import Message


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
            self._units[unit.name].start()

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
        self._units['tasker'] = Tasker(self)

        # LIGHT UNITS
        self._units['http'] = HTTP(self)
        self._units['http'].start()

        # NEW LAYERS (EXECUTORS)
        for lid in range(0, self.layers):
            self._executors[lid] = Executor(self, lid)
            self._executors[lid].start()

        self._units['tasker'].start()
        
        for unit in self._units.values():
            if unit.light:
                msg = {'dst':unit.name, 'src':'core', 'cmd':'register', 'params':{}, 'async':False}
                self.dispatch(msg)

        self._units['tasker'].logic.start()

    ''' ############################################
    '''
    def forward(self, message):

        print('[core.forward] {0}'.format(Message(message)))

        ''' This condition is for cases where one unit send
            a message to another one in the same layer.
        '''
        if not 'layer' in message:
            message['layer'] = self.layer

        if not 'jump' in message:
            message['jump'] = message['src']

        if message['layer'] == self.layer:
            if self._units[message['dst']].light and (message['jump'] != 'executor'):
                message['jump'] = 'executor'
                return self._executors[self.layer].dispatch(message)
            else:
                return self._units[message['dst']].dispatch(message)
        
        message['jump'] = 'executor'
        return self._executors[message['layer']].dispatch(message)


    ''' ############################################
        Core Unit Commands
        ############################################
    '''
    def halt(self, message):
        print('[core:{0}] Halting Layer ...'.format(self.layer))
        return {'status':0}

    def response(self, message):
        print('[core:{0}] Response: {1}'.format(self.layer, message))
        return {'status':0}
        
    def schedule(self, message):
        #print('[core.schedule] message: {0}'.format(message))
        params = message['params']
        
        ''' This is called, for example when a layer should be
            discharged, to flush all the pending messages to
            the layer 0.
        '''
        '''
        if 'layer' in params:
            try:
                layer = params['layer']
                for msg in params['message']:
                    msg['layer'] = layer
                    self._executors[layer].dispatch(msg)
            except KeyError:
                return {'error':'-1', 'msg':'Layer {0} does not exist'.format(layer)}
        else:
        '''
        ''' If we have to schedule messages from a leyer 
            higher than 0, first we forward the schedule message to
            the layer 0 to make the layer digest it. This is because
            the 'layers' variable would be only updated in layer 0, not
            necessarily in all layers. For example, when you append new
            layers, these are copies of layer 0, so just layer 0 and new others
            known the real number of working layers.
        '''
        msg = params['message']
        if self.layer:
            result = self._executors[0].dispatch(message)

        elif ('layer' in msg) and (msg['layer'] >= self.layers):
            return {'status':-1}

        else:
            msg['layer'] = random.randint(0, self.layers - 1)
            msg['jump']  = 'executor'
            result = self._executors[msg['layer']].dispatch(msg)

        return result
