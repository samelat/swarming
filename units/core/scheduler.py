
from Threading import Queue, Condition

from units.core.task import Task


class Scheduler:

    def __init__(self, core):
        self._core = core

        self._messages = Queue()
        self._units = {}
        self._tasks = {1,2,3,4}
        self._tlock = Condition()

    ''' 
    '''
    def _handler(self):
        while not self.halt:
            try:
                message = self._messages.get(timeout=1)
            except queue.Empty:
                continue

            self._tlock.acquire()
            while not (len(self._tasks) or self.halt):
                self._tlock.wait(timeout=1)

            if self.halt:
                self._tlock.release()
                break

            task_id = self._tasks.pop()
            self._tlock.release()

            # We change the message dest to redirect it to his new unit
            uname, _  = message['dst']
            message['dst'] = (uname, task_id)

            unit_zero = self._tasks[uname][0]
            self._tasks[uname][task_id] = Task(self._core, unit_zero, task_id)
            self._tasks[uname][task_id].start()

            self._tasks[uname][task_id].dispatch(message)


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
        # Unit name, Task ID
        uname, tid = unit.name()

        if uname not in self._units:
            self._units[uname] = {0:unit}
        else:
            tid = self._tasks.pop()
            self._units[uname][tid] = unit

        return (uname, tid)

    def forward(self, message):
        uname, tid = message['dst']
        try:
            self._units[uname][tid].dispatch(message)
        except:
            pass
            # TODO: We could generate a error here, informing that
            #       the dst module does not exist.


    ''' ############################################
        Commands
    '''
    '''
    def schedule(self, message):
        print('[core] Scheduling: {0}'.format(message))
        self._messages.put(message['param']['message'])
        return {'state':'scheduled'}
    '''

    def wait_sunit(self, message):
        print('[core] Waiting for task {0}'.format(message))
        return {'state':'done'}
