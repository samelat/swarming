
from units.modules.unit import Unit


class LightUnit(Unit):

    light = True

    def __init__(self, core):
        super(LightUnit, self).__init__(core)

        self.stages  = {}
        self.message = None

        self.add_cmd_handler('consume', self.consume)


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
        self.register()


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
                return {'error':-1, 'msg':'Unknown stage'}

        result = where['*'](message)

        return result

    ''' 
    '''
    def persist(self, values):
        message = {'dst':message['src'], 'src':self.name,
                   'cmd':'set', 'params':{'values':{'id':task['id'],
                                                    'stage':'crawling',
                                                    'state':'stopped'},
                                          'table':'task'}}
        self.dispatch(message)