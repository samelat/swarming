
import time
import socket
import requests

from units.http.tools import HTML
from units.http.crawler.container import Container
from units.http.crawler import spiders


class Crawler:

    request_attempts = 3

    def __init__(self, unit):
        self.unit = unit

        # This list of Spiders has been ordered. Don't change its order.
        self.spiders = {'app:'spiders.AppSpider(unit),
                        'error':spiders.ErrorSpider(unit),
                        'default':spiders.DefaultSpider(unit)}
        self.container = None
        self.timestamp = time.time()

        '''
        self.status_codes = set()
        self.content_types = set()
        for spider in self.spiders:
            self.status_codes.update(spider.status_codes)
            self.content_types.update(spider.content_types)
        '''

    ''' Each unit is responsable of the 'done' and 'total'
        values update. That is what this method do.
    '''
    def sync(self, component, force=False):
        timestamp = time.time()
        if force or (timestamp > (self.timestamp + 4.0)):
            self.timestamp = timestamp

            done = self.container.done()
            total = self.container.total()

            self.unit.set_knowledge({'task':{'id':self.unit.task['id'],
                                             'done':done,
                                             'total':total}})

    def is_interesting(self, request):
        head_request = request.copy()
        head_request['method'] = 'head'

        # TODO: Try to detect if It's a valid resource analyzing the extension

        response = self.session.request(**head_request)

        content = self.get_content(response, digest=False)
        if content['content-type'] in self.content_types:
            return True

        if response.status_code in self.status_codes:
            return True

        return False


    def get_content(self, response, digest=True):
        content = {'content-type':'text/plain'}
        if 'content-type' in response.headers:
            content['content-type'] = response.headers['content-type'].split(';')[0]

        if not digest:
            return content

        if content['content-type'] == 'text/html':
            content['html'] = HTML(response.text)

        return content

    '''

    '''
    def crawl(self):

        print('[COMPLEMENT] {0} - {1}'.format(self.unit.url, self.unit.complements))

        result = {'status':0}

        self.container = Container(self.unit.url)
        self.session = requests.Session()
        
        for request in self.container:

            request['timeout'] = self.timeout
            request['allow_redirects'] = False
            request.update(self.unit.complements)

            print('[CRAWLER] next url: {0}'.format(request['url']))
            attempts = request_attempts
            while attempts:
                try:
                    head_request = request.copy()
                    head_request['method'] = 'head'
                    response = self.session.request(**request)
                    response = self.session.request(**request)

                    break

                except requests.exceptions.ConnectionError:
                    result = {'status':-1, 'task':{'state':'error', 'description':'Connection Error'}}

                except socket.timeout:
                    print('[!] Timeout: {0}'.format(request))
                    result = {'status':-2, 'task':{'state':'error', 'description':'No response'}}

                attempts += 1

            #except:
            #    print('[crawler] Error requesting {0}'.format(request))
            #    continue

            print('[CRAWLER] CODE: {0}'.format(response.status_code))

            content = self.get_content(response)

            for spider_name, spider in self.spiders.items():
                if not spider.accept(response, content):
                    continue

                result = spider.parse(request, response, content)

                if 'requests' in result:
                    for _request in result['requests']:
                        self.container.add_request(_request)

                if 'filters' in result:
                    for _filter in result['filters']:
                        self.container.add_filter(_filter)

                if 'dictionaries' in result:
                    for dictionary in result['dictionaries']:
                        pass
                        #print('[http.crawler] new dictionary: {0}'.format(dictionary))

                if ('break' in result) and (result['break']):
                    break

            # Syncronize the total and done work
            self.sync(self)

        self.session = None
        self.sync(self, True)

        return result
