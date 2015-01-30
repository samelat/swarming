
import time

from units.modules import tools
from units.modules.light_unit import LightUnit


class HTTP(LightUnit):

    name = 'http'
    protocols = ['http', 'https']

    def __init__(self, core):
        super(HTTP, self).__init__(core)

        self.add_stage_handler('initial', self.http_initial_stage)
        self.add_stage_handler('forcing', self.http_forcing_stage)
        self.add_stage_handler('crawling', self.http_crawling_stage)
        

    ''' ############################################
        Command & Stage handlers
    '''
    def http_initial_stage(self, message):
        print('[http] Initial Stage method')

        task = message['params']['task']

        values = {'task':{'id':task['id'], 'stage':'crawling', 'state':'stopped'}}

        print('[http] setting initial task values')
        self.set_knowledge(values, True)

        return {'status':0}

    '''

    '''
    def http_forcing_stage(self, message):
        print('HTTP Forcing Stage method')
        for c in range(1, 7):
            print('[http] Forcing cicle {0}'.format(c))
            time.sleep(4)

        return {'status':0}

    '''

    '''
    def http_crawling_stage(self, message):
        print('HTTP Crawling Stage method')
        for c in range(1, 7):
            print('[http] Crawling cicle {0}'.format(c))
            time.sleep(4)

        values = {'task':{'id':task['id'], 'stage':'crawling', 'state':'complete'}}

        self.dispatch(message)

        return {'status':0}
