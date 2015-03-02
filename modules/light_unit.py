
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


    def success(self, credentials, complement):

        rows = {'success':{'credentials':credentials, 'task':{'id':self.task['id']}}}
        if not 'complement' in self.task:
            self.task['complement'] = complement
            rows['complement'] = {'values':complement, 'task':{'id':self.task['id']}}

        self.set_knowledge(rows)


    def consume(self, message):
        try:
            self.task = message['params']['task']

            if 'complements' in message['params']:
                self.complements = message['params']['complements']

            self.prepare()

            stage = self.task['stage']
            result = self.stages[stage](message)
        except KeyError:
            return {'status':-1, 'error':'Unknown stage'}

        return result

    ''' 
    '''
    # TODO: Move this method to LightUnit
    def register(self, message):

        support = [{'unit':{'name':self.name, 'protocol':protocol}} for protocol in self.protocols]
        result = self.set_knowledge(rows=support)

        #print('[{0}.register] REGISTRATION RESULT: {1}'.format(self.name, result))

        return {'status':0}