
import time
import traceback

from common.unit import Unit


class LightUnit(Unit):

    name = None
    light = True

    def __init__(self, core):
        super(LightUnit, self).__init__(core)

        self.task = None
        self.stages = {}
        self.registers = []
        self.timestamp = 0

        self.add_cmd_handler('consume', self.consume)
        self.add_cmd_handler('register', self.register)

    @classmethod
    def build(cls, core):
        core.units[cls.name] = cls(core)
        core.units[cls.name].start()
        return {'status': 0}

    # Once the message was received, this method is called
    def prepare(self):
        pass

    # This method execute "command" over engine using the specified parameters.
    def engine(self, command, params, block=False):
        message = {'src': self.name, 'dst': 'engine', 'cmd': command, 'params': params}
        result = self.core.dispatch(message)

        if block:
            result = self.get_response(result['channel'], True)

        return result

    def success(self, credentials, complement=None):
        print('[!!!] Success: {0} - Logs: {1}'.format(credentials, complement))

        '''
        rows = {'success': {'credentials': credentials, 'task': {'id': self.task['id']}}}
        if 'complement' not in self.task:
            if complement:
                self.task['complement'] = complement

            rows['complement'] = {'values': complement, 'task': {'id': self.task['id']}}

        self.knowledge()
        '''

        return {'status': 0}

    ############################################
    #              Unit Commands               #
    ############################################
    def consume(self, message):
        try:
            self.task = message['params']['task']
            self.registers = message['params']['registers']

            if not self.task['port']:
                self.task['port'] = self.protocols[self.task['protocol']]
                self.engine('put', {'entity': 'task', 'entries': {'id': self.task['id'], 'port': self.task['port']}})

            self.prepare()

            result = self.stages[self.task['stage']](message)

        except KeyError:
            return {'status': -1, 'error': 'Unknown stage'}

        return result

    def register(self, message):

        entries = [{'name': self.name, 'protocol': protocol, 'port': port} for protocol, port in self.protocols.items()]
        self.engine('post', {'entity': 'unit', 'entries': entries}, True)

        return {'status': 0}
