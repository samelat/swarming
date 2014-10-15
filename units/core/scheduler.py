
import queue
from threading import Condition

from units.core.task import Task


class Scheduler:

    def __init__(self, core):
        self._core = core
        self._halt = False

        self._to_schedule = queue.Queue()

    ''' 
    '''
    def _handler(self):
        nlid = 1
        while not self._halt:
            try:
                message = self._to_schedule.get(timeout=1)
            except queue.Empty:
                continue

            print('[scheduler] Message {0} - Layer ID {1}'.format(message, nlid))

            # We change the message dest to redirect it to a new Executor
            uname, _  = message['dst'].split(':')
            message['dst'] = '{0}:{1}'.format(uname, nlid)

            self._executors[neid].dispatch(message)

            if neid > Scheduler.executors:
                neid = 1
        print('[scheduler] stopped')


    def start(self):
        self._handler()

    def halt(self):
        print('[core] Broadcasting "halt" message...')

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
