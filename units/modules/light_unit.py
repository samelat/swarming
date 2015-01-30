
from units.modules.unit import Unit


class LightUnit(Unit):

    light = True

    def __init__(self, core):
        super(LightUnit, self).__init__(core)

        self.stages  = {}
        self.message = None

        self.add_cmd_handler('consume', self.consume)
        self.add_cmd_handler('register', self.register)


    def add_stage_handler(self, stage, handler):
        _stage = stage.split('.')
        if _stage[-1] == '*':
            _stage.pop()
        
        where = self.stages
        for stage in _stage:
            try:
                where = where[stage]
            except KeyError:
                where[stage] = {}
                where = where[stage]

        where['*'] = handler


    def start(self):
        print('[{0}] Starting'.format(self.name))
        #self.register()


    def consume(self, message):

        self.message = message

        task = message['params']['task']
        stage = task['stage'].split('.')
        if stage[-1] == '*':
            stage.pop()

        where = self.stages
        for stage in stage:
            try:
                where = where[stage]
            except KeyError:
                return {'status':-1, 'msg':'Unknown stage'}

        result = where['*'](message)

        return result

    ''' 
    '''
    # TODO: Move this method to LightUnit
    def register(self, message):
        values = {'name':self.name,
                  'protocols':[{'name':protocol} for protocol in self.protocols]}
        result = self.set_knowledge(values)
        print('[{0}.register] REGISTRATION RESULT: {1}'.format(self.name, result))

        return {'status':0}