
import time
import requests

from units.http.tools import HTML
from units.http.crawler.container import Container
from units.http.crawler import spiders


class Crawler:

    def __init__(self, unit):
        self.unit = unit

        # This list of Spiders has been ordered. Don't change its order.
        self.spiders = [spiders.ErrorSpider(unit),
                        spiders.AppSpider(unit),
                        spiders.DefaultSpider(unit)]
        self.container = None
        self.timestamp = time.time()

        self.content_types = set()
        for spider in self.spiders:
            self.content_types.update(spider.content_types)

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
        if response.headers['content-type'].split(';')[0] in self.content_types:
            return True

        return False

    '''

    '''
    def crawl(self):

        print('[COMPLEMENT] {0} - {1}'.format(self.unit.url, self.unit.complements))

        self.container = Container(self.unit.url)
        self.session = requests.Session()
        
        for request in self.container:

            request['allow_redirects'] = False
            request.update(self.unit.complements)

            print('[CRAWLER] next url: {0}'.format(request['url']))
            try:
                if not self.is_interesting(request):
                    continue
                response = self.session.request(**request)

            except requests.exceptions.ConnectionError:
                return {'status':-1, 'task':{'state':'error', 'description':'Connection Error'}}

            #except:
            #    print('[crawler] Error requesting {0}'.format(request))
            #    continue

            extra = {'content-type':response.headers['content-type'].split(';')[0]}
            if 'text/html' == extra['content-type']:
                extra['html'] = HTML(response.text)

            for spider in self.spiders:
                if not spider.accept(response, extra):
                    continue

                result = spider.parse(request, response, extra)

                #print(result)

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

        return {'status':0}
