
import time
import urllib
import requests
import traceback

import logging

from common.light_unit import LightUnit

from units.http import cracker
from units.http.crawler import crawler


class HTTP(LightUnit):

    name = 'http'
    protocols = {'http': 80,
                 'https': 443}

    def __init__(self, core):
        super(HTTP, self).__init__(core)

        self.url = None
        self.logger = logging.getLogger(__name__)
        self.logger.info('Starting HTTP unit ...')

        self.request = {}
        self.crackers = {'get': cracker.Get,
                         'post': cracker.Post,
                         'basic': cracker.BasicAuth}

        self.stages['initial'] = self.http_initial_stage
        self.stages['crawling'] = self.http_crawling_stage
        self.stages['cracking.dictionary'] = self.http_cracking_stage

    # This method exist to prepare the context for the stage handler execution.
    def prepare(self):

        '''
        auth = None
        if 'auth' in self.task['attrs']:
            auth = self.task['attrs']['auth']

        if auth:
            if auth['method'] == 'basic':
                self.request['auth'] = (auth['username'], auth['password'])

            elif auth['method'] == 'digest':
                self.logger.error('Digest authentication not supported')

        self.url = '{protocol}://{0}{path}'.format(netloc, **self.task)
        if 'query' in self.task['attrs']:
            self.url += self.task['attrs']['query']

        # If task and protocol ports are the same, we ignore it
        netloc = self.task['hostname']
        if self.task['port'] != self.protocols[self.task['protocol']]:
            netloc += ':{0}'.format(self.task['port'])
        '''

    ''' ############################################
        Command & Stage handlers
    '''
    def http_initial_stage(self, message):
        print('[http] Initial Stage method')

        print('[http] {0}'.format(message))

        # We return in 'updates' the self task values we want to change.
        self.task.update({'stage':'crawling', 'state':'ready', 'description':'Web Crawling'})

        try:
            response = requests.request(method='head', url=self.url, verify=False)
        except requests.exceptions.ConnectionError:
            return {'status':-1, 'error':'Connection Error'}

        # TODO: Control connection errors
        '''
        if response.status_code != 200:
            return {'status':-1, 'task':{'stage':'error', 'state':'stopped',
                                         'description':'HTTP Error {0}'.format(response.status_code)}}
        '''

        url = urllib.parse.urlsplit(response.url)
        if url.hostname != self.task['hostname']:
            # print('[HTTP_INIT] Hostnames: {0} - {1}'.format(url.hostname, self.task['hostname']))
            return {'status':-2, 'error':'HTTP Redirection'}

        if url.scheme != self.task['protocol']:
            self.task['protocol'] = url.scheme
            if not url.port:
                self.task['port'] = self.protocols[url.scheme]

        self.set_knowledge({'task':self.task})

        return {'status':0}

    ''' 
    '''
    def http_cracking_stage(self, message):
        auth_scheme = self.task['attrs']['auth_scheme']
        try:
            _cracker = self.crackers[auth_scheme](self)
            result = _cracker.crack(message['params']['dictionaries'])

        except KeyError:
            traceback.print_exc()
            return {'status': -1, 'error': 'Unknown Authentication Scheme "{0}"'.format(auth_scheme)}

        return result

    ''' 
    '''
    def http_crawling_stage(self, message):
        try:
            _crawler = crawler.Crawler(self)
            result = _crawler.crawl()
            
        except KeyError:
            traceback.print_exc()
            return {'status':-1}
        return result

