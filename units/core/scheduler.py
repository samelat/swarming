
import queue
from threading import Condition

from units.core.task import Task


class Scheduler:

    def __init__(self, core):
        self._core = core
        self._halt = False

        self._to_schedule = queue.Queue()
        self._units = {}
        self._tasks = {'1','2','3','4'}
        self._tlock = Condition()

    ''' 
    '''
    def _handler(self):
        while not self._halt:
            try:
                message = self._to_schedule.get(timeout=1)
            except queue.Empty:
                continue

            self._tlock.acquire()
            while not (len(self._tasks) or self._halt):
                self._tlock.wait(timeout=1)

            if self._halt:
                self._tlock.release()
                break

            task_id = self._tasks.pop()
            self._tlock.release()

            print('[scheduler] Message {0} - Task ID: {1}'.format(message, task_id))

            # We change the message dest to redirect it to a new unit
            uname, _  = message['dst'].split(':')
            message['dst'] = '{0}:{1}'.format(uname, task_id)

            unit_zero = self._units[uname]['0']
            self._units[uname][task_id] = Task(self._core, unit_zero, task_id)
            self._units[uname][task_id].start()

            self._units[uname][task_id].dispatch(message)
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
    
    def add_zero_unit(self, unit):
        # Unit name, Task ID

        if unit.name not in self._units:
            self._units[unit.name] = {'0':unit}

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
            self._units[uname][tid].dispatch(message)
        except:
            pass
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
