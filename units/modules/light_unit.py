
from units.modules.unit import Unit


class LightUnit(Unit):

    def __init__(self, core):
        super(LightUnit, self).__init__(core)

        self.stages = {}


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
        self.add_cmd_handler('digest', self.digest)


    def digest(self, message):

        task = message['params']['task']
        stage = task['stage'].split('.')
        if stage[-1] == '*':
            stage.pop()

        where = self.stages
        for stage in stage:
            try:
                where = where[stage]
            except KeyError:
                return {'status':'error', 'msg':'Unknown stage'}

        result = where['*'](message)

        return result