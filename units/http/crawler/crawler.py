
import time
import requests

from units.http.tools import HTML
from units.http.crawler.container import Container
from units.http.crawler import spiders


class Crawler:

    def __init__(self, unit):
        self.unit = unit
        self.spiders = [spiders.MainSpider(unit),
                        spiders.ErrorSpider(unit),
                        spiders.AppSpider(unit)]
        self.container = None
        self.timestamp = time.time()

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

    '''

    '''
    def crawl(self):

        print('[COMPLEMENT] {0} - {1}'.format(self.unit.url, self.unit.complements))

        self.container = Container(self.unit.url)
        session = requests.Session()
        
        for request in self.container:

            request['allow_redirects'] = False
            request.update(self.unit.complements)

            print('[CRAWLER] next url: {0}'.format(request['url']))

            try:
                response = session.request(**request)
            except:
                print('[crawler] Error requesting {0}'.format(request))
                continue

            extra = {'content-type':response.headers['content-type'].split(';')[0]}
            if 'text/html' == extra['content-type']:
                extra['html'] = HTML(response.text)

            for spider in self.spiders:
                if not spider.accept(response, extra):
                    continue

                result = spider.parse(request, response, extra)

                print(result)

                if 'requests' in result:
                    for _request in result['requests']:
                        self.container.add_request(_request)

                if 'filters' in result:
                    for _filter in result['filters']:
                        self.container.add_filter(_filter)

                if 'dictionaries' in result:
                    for dictionary in result['dictionaries']:
                        print('[http.crawler] new dictionary: {0}'.format(dictionary))

            # Syncronize the total and done work
            self.sync(self)

        self.sync(self, True)

        return {'status':0}
