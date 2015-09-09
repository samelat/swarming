
import time
import logging
import requests
import mimetypes
from urllib import parse

from units.http.crawler.container import Container
from units.http.crawler import spiders

from units.http.support import HTML
from units.http.support import Protocol


class Crawler(Protocol):

    def __init__(self, unit):
        super().__init__()
        self.unit = unit
        self.logger = logging.getLogger(__name__)

        # The list of domains in which crawler are interested
        self.domains = set([parse.urlparse(self.unit.url).hostname])
        # This list of Spiders has been ordered. Don't change its order.
        self.spiders = {'app':spiders.AppSpider(unit),
                        'error':spiders.ErrorSpider(unit),
                        'default':spiders.DefaultSpider(unit)}
        self.container = None
        self.timestamp = time.time()

        # This flag existis beacause some servers do not respond with the
        # same status_code|content-type to HEAD and GET requests.
        self.use_head_content = True

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


    def get_content(self, request, response):

        content = {'content-type':'text/html', 'status-code':200}

        # I don't know why "requests" developers thought that an Error
        # response (404, ...) should be taken as False during bool(response) :S.
        if response != None:
            #content['content-type'] = 'text/plain'
            content['status-code'] = response.status_code
            if 'content-type' in response.headers:
                content['content-type'] = response.headers['content-type'].split(';')[0]

            if content['content-type'] == 'text/html':
                content['html'] = HTML(response.text)

        else:
            content_type, _ = self.mimetypes.guess_type(request['url'])
            if content_type:
                content['content-type'] = content_type

        return content

    ''' TODO:

    '''
    def add_request(self, request):
        url = parse.urlparse(request['url'])
        if url.scheme not in ['http', 'https']:
            return

        if url.hostname in self.domains:
            self.container.add_request(request)

    ''' 

    '''
    def crawl(self):

        crawl_result = {'status':0}

        self.container = Container({'method':'get', 'url':self.unit.url})
        self.session = requests.Session()
        
        for request in self.container:

            request['timeout'] = 16
            request['allow_redirects'] = False
            request.update(self.unit.complements)
            
            # Take the content-type to check if It is interesting for any spider
            response = None
            if self.use_head_content:
                head_request = request.copy()
                head_request['method'] = 'head'
                result, response = self.request(head_request)
                if result['status'] < 0:
                    crawl_result = result
                    break

            thin_content = self.get_content(request, response)

            interested_spiders = False
            for spider in self.spiders.values():
                if spider.accept(thin_content):
                    interested_spiders = True
                    break

            if not interested_spiders:
                continue

            # Make the original (complete) request
            result, response = self.request(request)
            if result['status'] < 0:
                crawl_result = result
                break

            thick_content = self.get_content(request, response)

            # Here we check if the thin_content got by HEAD, is working properly or not;
            # If not, we stop using It.
            if self.use_head_content:
                if (thick_content['status-code'] != thin_content['status-code']) or\
                   (thick_content['content-type'] != thin_content['content-type']):
                    self.use_head_content = False

            self.logger.debug('status-code: {0} - url: {1}'.format(thick_content['status-code'], request['url']))

            for spider_name, spider in self.spiders.items():
                if not spider.accept(thick_content):
                    continue

                result = spider.parse(request, response, thick_content)

                if 'requests' in result:
                    for _request in result['requests']:
                        self.add_request(_request)

                if 'filters' in result:
                    for _filter in result['filters']:
                        self.container.add_filter(_filter)

                if 'dictionaries' in result:
                    for dictionary in result['dictionaries']:
                        pass
                        #print('[http.crawler] new dictionary: {0}'.format(dictionary))

            # Syncronize the total and done work
            self.sync(self)

        print('[!] Crawl result {0}'.format(crawl_result))

        self.session = None
        self.sync(self, True)

        return crawl_result
