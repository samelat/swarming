
import queue
from threading import Condition

from units.core.task import Task


class Scheduler:

    def __init__(self, core):
        self._core = core
        self._halt = False

        self.units = {}

        self._to_schedule = queue.Queue()
        
        self._tasks = {}
        self._ntid = 1 # Next Task ID

    ''' 
    '''
    def _handler(self):
        while not self._halt:
            try:
                message = self._to_schedule.get(timeout=1)
            except queue.Empty:
                continue

            print('[scheduler] Message {0} - Task ID {1}'.format(message, self._ntid))

            # We change the message dest to redirect it to a new unit
            uname, _  = message['dst'].split(':')
            message['dst'] = '{0}:{1}'.format(uname, self._ntid)

            unit_zero = self._units[uname]['0']
            self._units[uname][self._ntid] = Task(self._core, unit_zero, self._ntid)
            self._units[uname][self._ntid].start()

            self._units[uname][self._ntid].dispatch(message)
        print('[scheduler] stopped')


    def start(self):
        print('[core] Starting all standard units...')
        for uname in self._units:
            for tid in self._units[uname]:
                self._units[uname][tid].start()
        self._handler()

    def halt(self):
        print('[core] Broadcasting "halt" message...')
        '''
        for unit_name in self.units.items():
            cmsg = message.copy()
            cmsg['dst'] = unit_name
            print('[core] Sending from "halt" message: {0}'.format(cmsg))
            unit.dispatch(cmsg)
            unit.wait()
        '''
    
    def add_unit(self, unit):
        if unit.name not in self.units:
            self.units[unit.name] = unit

            # If it is a border unit we register it
            if unit.is_border_unit:
                message = {'dst':'brain:0',
                           'cmd':'add',
                           'params':{'table_name':'border_unit',
                                     'values':{'name':unit.name,
                                               'protocols':unit.protocols}}}
                self._core.dispatch(message)

    def forward(self, message):
        uname, tid = message['dst'].split(':')
        try:
            unit = self.units[uname]
            if unit.is_border_unit or (tid == '0'):
                self._tasks[tid].dispatch(message)

            # In this case we have to inform that you cannot
            # dispatch a message to a basic unit other than '0'.
        except:
            print('[scheduler] exception')
            # TODO: We could generate a error here, informing that
            #       the dst module does not exist.


    ''' ############################################
        Commands
    '''
    def schedule(self, params):
        print('[core] Scheduling: {0}'.format(params))
        self._to_schedule.put(params['message'])
        return {'state':'done'}

    def wait_sunit(self, params):
        print('[core] Waiting for task {0}'.format(params))
        return {'state':'done'}
