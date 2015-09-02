
import time
import socket
import requests
import mimetypes

from units.http.tools import HTML
from units.http.crawler.container import Container
from units.http.crawler import spiders


class Crawler:

    request_attempts = 3

    def __init__(self, unit):
        self.unit = unit

        # This list of Spiders has been ordered. Don't change its order.
        self.spiders = {'app':spiders.AppSpider(unit),
                        'error':spiders.ErrorSpider(unit),
                        'default':spiders.DefaultSpider(unit)}
        self.container = None
        self.timestamp = time.time()

        self.mimetypes = mimetypes.MimeTypes()
        self.mimetypes.read('data/mime.types')

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

    def request(self, request):
        result = {'status':0}
        response = None

        attempts = self.request_attempts
        while attempts:
            try:
                response = self.session.request(**request)
                break

            except requests.exceptions.ConnectionError:
                result = {'status':-1, 'task':{'state':'error', 'description':'Connection Error'}}

            except socket.timeout:
                print('[!] Timeout: {0}'.format(request))
                result = {'status':-2, 'task':{'state':'error', 'description':'No response'}}

            attempts -= 1

        return result, response


    def get_content(self, request, response=None):

        content = {'status-code':200}

        if response:
            content['content-type'] = 'text/plain'
            content['status-code'] = response.status_code
            if 'content-type' in response.headers:
                content['content-type'] = response.headers['content-type'].split(';')[0]

            if content['content-type'] == 'text/html':
                content['html'] = HTML(response.text)

        if 'content-type' not in content:
            content_type, _ = self.mimetypes.guess_type(request['url'])
            if content_type:
                content['content-type'] = content_type

        return content

    ''' 

    '''
    def crawl(self):

        crawl_result = {'status':0}

        print('[COMPLEMENT] {0} - {1}'.format(self.unit.url, self.unit.complements))

        self.container = Container(self.unit.url)
        self.session = requests.Session()
        
        for request in self.container:

            request['timeout'] = 16
            request['allow_redirects'] = False
            request.update(self.unit.complements)

            print('[CRAWLER] next url: {0}'.format(request['url']))
            
            # Take the content-type to check if It is interesting for any spider
            content = self.get_content(request)
            if 'content-type' not in content:
                head_request = request.copy()
                head_request['method'] = 'head'
                result, response = self.request(head_request)
                if result['status'] < 0:
                    crawl_result = result
                    break

                content = self.get_content(request, response)

            interested_spiders = {}
            for spider_name, spider in self.spiders.items():
                if spider.accept(content):
                    interested_spiders[spider_name] = spider

            print(interested_spiders)

            if not interested_spiders:
                continue

            # Make the original (complete) request
            result, response = self.request(request)
            if result['status'] < 0:
                crawl_result = result
                break

            print('[CRAWLER] CODE: {0}'.format(response.status_code))

            for spider_name, spider in interested_spiders.items():
                if not spider.accept(content):
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

        return crawl_result
