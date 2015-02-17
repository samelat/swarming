
from units.modules.unit import Unit


class LightUnit(Unit):

    light = True

    def __init__(self, core):
        super(LightUnit, self).__init__(core)

        self.task = None
        self.resource = None
        self.stages  = {}

        self.add_cmd_handler('consume', self.consume)
        self.add_cmd_handler('register', self.register)


    def start(self):
        print('[{0}] Starting'.format(self.name))
        #self.register()


    def consume(self, message):

        try:
            self.task = message['params']['task']
            self.resource = self.task['resource']

            stage = self.task['stage']
            result = self.stages[stage](message)
        except KeyError:
            return {'status':-1, 'error':'Unknown stage'}

        return result

    ''' 
    '''
    # TODO: Move this method to LightUnit
    def register(self, message):

        for protocol in self.protocols:
            result = self.set_knowledge({'unit':{'name':self.name, 'protocol':protocol}})

        #print('[{0}.register] REGISTRATION RESULT: {1}'.format(self.name, result))

        return {'status':0}