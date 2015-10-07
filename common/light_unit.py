
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

    def sync(self, component, force=False):
        timestamp = time.time()
        if force or (timestamp > (self.timestamp + 4.0)):
            self.timestamp = timestamp

            done = component.get_done_work()
            total = component.get_total_work()

            self.set_knowledge({'task': {'id': self.task['id'],
                                         'done': done,
                                         'total': total}})

    def success(self, credentials, complement=None):
        print('[!!!] Success: {0} - Logs: {1}'.format(credentials, complement))
        return

        rows = {'success': {'credentials': credentials, 'task': {'id': self.task['id']}}}
        if 'complement' not in self.task:
            if complement:
                self.task['complement'] = complement

            rows['complement'] = {'values': complement, 'task': {'id': self.task['id']}}

        self.set_knowledge(rows)

    ############################################
    #              Unit Commands               #
    ############################################
    def consume(self, message):
        try:
            self.task = message['params']['task']
            self.registers = message['params']['registers']

            if not self.task['port']:
                self.task['port'] = self.protocols[self.task['protocol']]
                message = {'src': self.name, 'dst': 'engine', 'cmd': 'put',
                           'params': {'entity': 'task', 'entries': {'id': self.task['id'], 'port': self.task['port']}}}
                self.core.dispatch(message)

            self.prepare()

            result = self.stages[self.task['stage']](message)

        except KeyError:
            return {'status': -1, 'error': 'Unknown stage'}

        return result

    def register(self, message):

        entries = [{'name': self.name, 'protocol': protocol, 'port': port} for protocol, port in self.protocols.items()]
        message = {'src': self.name, 'dst': 'engine', 'cmd': 'post', 'params': {'entity': 'unit', 'entries': entries}}
        result = self.core.dispatch(message)

        # Wait until response arrive
        self.get_response(result['channel'], True)

        return {'status': 0}
