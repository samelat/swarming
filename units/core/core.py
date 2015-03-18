
import random
from threading import Condition

from modules.unit import Unit
from modules.message import Message

from units.http.http import HTTP
from units.engine.engine import Engine
from units.core.executor import Executor


class Core(Unit):

    name = 'core'

    def __init__(self):
        super(Core, self).__init__()
        # I have to change this to load the unit dinamicaly
        self._unit_class = {'executor':Executor,
                            'http':HTTP}
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

        # HEAVY UNITS
        self.units['engine'] = Engine(self)
        self.units['engine'].start()
        self.units['engine'].logic.start()

    ''' ############################################
        Messages Handlers
    '''
    def forward(self, message):

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
        return {'status':0}

    def response(self, message):
        return {'status':0}

    def control(self, message):

        self.acquire(True)

        params = message['params']
        if params['action'] == 'load':
            result = self._unit_class[params['unit']].build(self)

        elif params['action'] == 'drop':
            result = {'status':-1}

        elif params['action'] == 'reload':
            result = {'status':-1}
        
        self.release(True)

        return result