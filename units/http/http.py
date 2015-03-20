
import time
import urllib
import requests
import traceback

from modules.light_unit import LightUnit

from units.http import cracker
from units.http.crawler import crawler


class HTTP(LightUnit):

    name = 'http'
    protocols = {'http' :80,
                 'https':443}

    def __init__(self, core):
        super(HTTP, self).__init__(core)

        self.url = None

        self.crackers = {'get':cracker.Get,
                         'post':cracker.Post,
                         'basic':cracker.BasicAuth}

        self.stages['initial']  = self.http_initial_stage
        self.stages['crawling'] = self.http_crawling_stage
        self.stages['cracking.dictionary']  = self.http_cracking_stage


    # This method exist to adapt the dependencies to Unit needs
    def prepare(self):
        if 'auth' in self.complements:
            self.complements['auth'] = tuple(self.complements['auth'])

        # If the task's port is the protocol defaul port, we do not add it
        netloc = self.task['hostname']
        if self.task['port'] != self.protocols[self.task['protocol']]:
            netloc += ':{0}'.format(self.task['port'])

        self.url = '{protocol}://{0}{path}'.format(netloc, **self.task)
        if 'query' in self.task['attrs']:
            self.url += self.task['attrs']['query']
        

    ''' ############################################
        Command & Stage handlers
    '''
    def http_initial_stage(self, message):
        print('[http] Initial Stage method')

        # We return in 'updates' the self task values we want to change.
        values = {'stage':'crawling', 'state':'ready'}

        response = requests.request(method='head', url=self.url)

        if response.status_code != 200:
            return {'status':-1, 'task':{'stage':'error', 'state':'stopped',
                                         'description':'HTTP Error {0}'.format(response.status_code)}}

        url = urllib.parse.urlsplit(response.url)

        if url.hostname != self.task['hostname']:
            print('[HTTP_INIT] Hostnames: {0} - {1}'.format(url.hostname, self.task['hostname']))
            return {'status':-2, 'task':{'stage':'error', 'state':'stopped',
                                         'description':'HTTP Redirection'}}

        if url.scheme != self.task['protocol']:
            values['protocol'] = url.scheme
            if not url.port:
                values['port'] = self.protocols[url.scheme]

        return {'status':0, 'task':values}

    ''' 
    '''
    def http_cracking_stage(self, message):
        print('HTTP Forcing Stage method')

        auth_scheme = self.task['attrs']['auth_scheme']
        try:
            _cracker = self.crackers[auth_scheme](self)

            result = _cracker.crack(message['params']['dictionaries'])
        except KeyError:
            traceback.print_exc()
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

        # new_task = {'task':{'stage':'cracking.dictionary', 'state':'stopped'}}
        # new_task['task']['resource'] = {'service':{'id':1}, 'attrs':{'auth_scheme':'basic'}, 'path':'/'}

        # self.set_knowledge(new_task, True)

        #values = {'task':{'id':task['id'], 'state':'complete'}}

        #self.set_knowledge(values, True)

        #return {'status':0, 'values':result}

        return {'status':0}
