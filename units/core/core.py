
import random
from threading import Condition

from modules.unit import Unit
from modules.message import Message

from units.ssh.ssh import SSH
from units.http.http import HTTP
from units.engine.engine import Engine
from units.core.executor import Executor


class Core(Unit):

    name = 'core'

    def __init__(self):
        super(Core, self).__init__()
        # I have to change this to load the unit dinamicaly
        self._unit_class = {'executor':Executor,
                            'http':HTTP,
                            'ssh':SSH}
        self._condition = Condition()
        self._accesses = 0

        self.units = {}
        self.executors = {}

        self.layer = 0


    def acquire(self, modify=False):
        self._condition.acquire()
        if modify:
            while self._accesses != 0:
                self._condition.wait()
            self._accesses = -1
        else:
            while self._accesses < 0:
                self._condition.wait()
            self._accesses += 1
        self._condition.release()


    def release(self, modify=False):
        self._condition.acquire()
        if modify:
            self._accesses = 0
        else:
            self._accesses -= 1
        self._condition.notify_all()
        self._condition.release()


    def clean(self):
        self._accesses = 0
        self.executors = {}
        units = {}
        for name, unit in self.units.items():
            unit.clean()
            units[name] = unit
        self.units = units


    ''' ############################################
    '''
    def start(self):
        self.add_cmd_handler('control', self.control)

        ''' TODO: It is better if we take the list of
            modules to load from a config file or something
            like that (do not hardcode them).
        '''
        ''' We have to follow this order in the units' declaration and 
            starting because in another way they will not exist in the
            different layers.
        '''
        # HEAVY UNITS
        self.units['engine'] = Engine(self)

        # LIGHT UNITS
        # self.units['http'] = HTTP(self)
        # self.units['http'].start()
        
        # NEW LAYERS (EXECUTORS)
        '''
        for lid in range(1, layers):
            self._executors[lid] = Executor(self, lid)
            self._executors[lid].start()
        '''

        self.units['engine'].start()

        '''
        for unit in self.units.values():
            if unit.light:
                msg = {'dst':unit.name, 'src':'core', 'cmd':'register', 'params':{}, 'async':False}
                self.dispatch(msg)
        '''
        
        self.units['engine'].logic.start()

    ''' ############################################
        Messages Handlers
    '''
    def forward(self, message):

        #print('[core.forward] {0}'.format(Message(message)))

        ''' This condition is for cases where one unit send
            a message to another one in the same layer.
        '''

        '''
        if not 'jump' in message:
            message['jump'] = message['src']


        if message['layer'] == self.layer:
            if self.units[message['dst']].light and (message['jump'] != 'executor'):
                message['jump'] = 'executor'
                return self._executors[self.layer].dispatch(message)
            else:
                return self.units[message['dst']].dispatch(message)
        
        message['jump'] = 'executor'
        return self._executors[message['layer']].dispatch(message)
        '''

        self.acquire()

        if (message['dst'] in self.units):
            if 'layer' not in message:
                message['layer'] = self.layer
            result = self.units[message['dst']].dispatch(message)
        elif self.layer == 0:
            if not self.executors:
                result = {'status':-2, 'msg':'No layers with Executors'}
            else:
                if 'layer' not in message:
                    message['layer'] = random.randint(1, len(self.executors))
                result = self.executors[message['layer']].dispatch(message)
        else:
            result = {'status':-1, 'msg':'Destination {0} unknown in layer {1}.'.format(message['dst'], self.layer)}

        self.release()

        return result
        

    ''' ############################################
    '''
    def digest(self, message):
        #print('[{0}.digest] {1}'.format(self.name, message))

        if (self.layer == 0) and ('layer' in message) and (message['layer'] != 0):
            self.acquire()
            result = self.executors[message['layer']].dispatch(message)
            self.release()

        else:
            result = super(Core, self).digest(message)

        return result


    ''' ############################################
        Core Unit Commands
        ############################################
    '''
    def halt(self, message):
        #print('[core:{0}] Halting Layer ...'.format(self.layer))
        return {'status':0}

    def response(self, message):
        #print('[core:{0}] Response: {1}'.format(self.layer, message))
        return {'status':0}

    def control(self, message):

        self.acquire(True)

        params = message['params']
        if params['action'] == 'load':
            #print(dir(self._unit_class[params['unit']]))
            result = self._unit_class[params['unit']].build(self)
            #print('[core.control:{0}] result: {1}'.format(self.layer, result))

        elif params['action'] == 'drop':
            result = {'status':-1}

        elif params['action'] == 'reload':
            result = {'status':-1}
        
        self.release(True)

        return result