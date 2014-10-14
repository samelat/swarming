
import queue
from threading import Condition

from units.core.task import Task


class Scheduler:

    executors = 4

    def __init__(self, core):
        self._core = core
        self._halt = False

        self._units = {}

        self._executors = {}

        self._to_schedule = queue.Queue()

    ''' 
    '''
    def _handler(self):
        neid = 1
        while not self._halt:
            try:
                message = self._to_schedule.get(timeout=1)
            except queue.Empty:
                continue

            print('[scheduler] Message {0} - Executor ID {1}'.format(message, self._neid))

            # We change the message dest to redirect it to a new Executor
            uname, _  = message['dst'].split(':')
            message['dst'] = '{0}:{1}'.format(uname, neid)

            self._executors[neid].dispatch(message)

            if neid > Scheduler.executors:
                neid = 1
        print('[scheduler] stopped')


    def start(self):
        print('[core] Starting all units...')
        for uname in self._units:
            self._units[uname].start()

        for eid in range(1, Scheduler.executors + 1):
            self._executors[eid] = Executor(self._core, eid)
            self._executors[eid].start()

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
        if unit.name not in self._units:
            self._units[unit.name] = unit

            # If it is a border unit we register it
            # TODO: Each module have to registers itself
            '''
            if unit.is_border_unit:
                message = {'dst':'brain:0',
                           'cmd':'add',
                           'params':{'table_name':'border_unit',
                                     'values':{'name':unit.name,
                                               'protocols':unit.protocols}}}
                self._core.dispatch(message)
            '''

    def forward(self, message):
        uname, eid = message['dst'].split(':')
        try:
            unit = self.units[uname]
            if unit.is_border_unit:
                if eid in self._executors:
                    self._executors[eid].dispatch(message)
                else:
                    unit.dispatch(message)
            elif eid == '0':
                unit.dispatch(message)
            else:
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
