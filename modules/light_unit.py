
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

        values = {}

        try:
            self.task = message['params']['task']

            if 'complements' in message['params']:
                self.complements = message['params']['complements']

            # self.task['done'] = 0
            # self.task['total'] = 0

            if not self.task['port']:
                values['port'] = self.task['port'] = self.protocols[self.task['protocol']]

            self.prepare()

            result = self.stages[self.task['stage']](message)

        except KeyError:
            return {'status':-1, 'error':'Unknown stage'}

        # Task Initialization.
        if 'task' in result:
            values.update(result['task'])

        if values:
            values['id'] = self.task['id']
            self.set_knowledge({'task':values})

        return {'status':result['status']}

    ''' ##########################################
    '''
    def register(self, message):

        support = [{'unit':{'name':self.name, 
                            'protocol':protocol,
                            'port':port}} for protocol, port in self.protocols.items()]
        result = self.set_knowledge(rows=support)

        return {'status':0}