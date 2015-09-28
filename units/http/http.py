
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
        self.logger = logging.getLogger(__name__)
        self.logger.info('Starting HTTP unit ...')

        self.url = None
        self.registers = []
        self.crackers = {'get': cracker.Get,
                         'post': cracker.Post,
                         'basic': cracker.BasicAuth}

        self.stages['initial'] = self.http_initial_stage
        self.stages['crawling'] = self.http_crawling_stage
        self.stages['cracking.dictionary'] = self.http_cracking_stage

    # This method exist to prepare the context for the stage handler execution.
    def prepare(self):

        self.registers = self.task['registers']

        port = ':{0}'.format(self.task['port']) if self.task['port'] not in self.protocols.values() else ''
        self.url = '{protocol}://{hostname}{0}{path}'.format(port, **self.task)

    ''' ############################################
        Command & Stage handlers
    '''
    def http_initial_stage(self, message):
        print('[http] Initial Stage method')
        print('[http] {0}'.format(message))

        # We return in 'updates' the self task values we want to change.
        self.task.update({'stage': 'crawling', 'state': 'ready', 'description': 'Web Crawling'})

        try:
            requests.request(method='head', url=self.url, verify=False)

        except requests.exceptions.ConnectionError:
            return {'status': -1, 'error': 'Connection Error'}

        return {'status': 0}

    ''' 
    '''
    def http_cracking_stage(self, message):
        try:
            auth_scheme = self.registers['auth_scheme']
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
            return {'status': -1}
        return result

