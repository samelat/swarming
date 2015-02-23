
import time
import traceback

from units.modules.light_unit import LightUnit

from units.http import cracker
from units.http.crawler import crawler


class HTTP(LightUnit):

    name = 'http'
    protocols = ['http', 'https']

    def __init__(self, core):
        super(HTTP, self).__init__(core)

        self.url = None

        self.crackers = {'get':cracker.Get,
                         'post':cracker.Post,
                         'basic':cracker.BasicAuth}

        self.stages['initial']  = self.http_initial_stage
        self.stages['crawling'] = self.http_crawling_stage
        self.stages['forcing.dictionary']  = self.http_forcing_stage


    # This method exist to adapt the dependencies to Unit needs
    def prepare(self):
        if 'auth' in self.complements:
            self.complements['auth'] = tuple(self.complements['auth'])

        self.url = '{protocol}://{hostname}:{port}{path}'.format(**self.task)
        if 'query' in self.task['attrs']:
            self.url += self.task['attrs']['query']
        

    ''' ############################################
        Command & Stage handlers
    '''
    def http_initial_stage(self, message):
        print('[http] Initial Stage method')

        values = {'task':{'id':self.task['id'], 'stage':'crawling', 'state':'ready'}}

        print('[http] setting initial task values')
        self.set_knowledge(values)

        return {'status':0}

    ''' 
    '''
    def http_forcing_stage(self, message):
        print('HTTP Forcing Stage method')

        auth_scheme = self.task['attrs']['auth_scheme']
        try:
            _cracker = self.crackers[auth_scheme](self)

            result = _cracker.crack(message['params']['dictionaries'])
        except KeyError:
            return {'status':-1, 'error':'Unknown Authentication Scheme "{0}"'.format(auth_scheme)}

        return result

    ''' 
    '''
    def http_crawling_stage(self, message):
        print('HTTP Crawling Stage method')

        try:
            _crawler = crawler.Crawler(self)
            
            result = _crawler.crawl()
        except KeyError:
            traceback.print_exc()
            return {'status':-1}

        # new_task = {'task':{'stage':'forcing.dictionary', 'state':'stopped'}}
        # new_task['task']['resource'] = {'service':{'id':1}, 'attrs':{'auth_scheme':'basic'}, 'path':'/'}

        # self.set_knowledge(new_task, True)

        #values = {'task':{'id':task['id'], 'state':'complete'}}

        #self.set_knowledge(values, True)

        #return {'status':0, 'values':result}

        return {'status':0}
