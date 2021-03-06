
from modules.unit import Unit


class LightUnit(Unit):

    light = True

    def __init__(self, core):
        super(LightUnit, self).__init__(core)

        self.task = None
        self.stages = {}
        self.complements = {}

        self.add_cmd_handler('consume', self.consume)
        self.add_cmd_handler('register', self.register)

    @classmethod
    def build(cls, core):
        core.units[cls.name] = cls(core)
        core.units[cls.name].start()
        return {'status':0}

    # Once the message was received, this method is called
    def prepare(self):
        pass

    def sync(self, component, force=False):
        timestamp = time.time()
        if force or (timestamp > (self.timestamp + 4.0)):
            self.timestamp = timestamp

            done = component.get_done_work()
            total = component.get_total_work()

            self.set_knowledge({'task':{'id':self.task['id'],
                                        'done':done,
                                        'total':total}})

    def success(self, credentials, complement=None):
        rows = {'success':{'credentials':credentials, 'task':{'id':self.task['id']}}}
        if not 'complement' in self.task:
            if complement:
                self.task['complement'] = complement
            else:
                self.task['complement'] = credentials

            rows['complement'] = {'values':complement, 'task':{'id':self.task['id']}}

        self.set_knowledge(rows)

    def consume(self, message):
        try:
            self.task = message['params']['task']

            if 'complements' in message['params']:
                self.complements = message['params']['complements']

            # self.task['done'] = 0
            # self.task['total'] = 0

            if not self.task['port']:
                self.task['port'] = self.protocols[self.task['protocol']]

            self.prepare()

            result = self.stages[self.task['stage']](message)

        except KeyError:
            return {'status':-1, 'error':'Unknown stage'}

        print(result)
        return result

    ''' ##########################################
    '''
    def register(self, message):

        support = [{'unit':{'name':self.name, 
                            'protocol':protocol,
                            'port':port}} for protocol, port in self.protocols.items()]
        result = self.set_knowledge(rows=support)

        return {'status':0}