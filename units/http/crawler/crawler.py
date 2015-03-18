
import requests

from units.http.tools import HTML
from units.http.crawler.container import Container
from units.http.crawler import spiders

import time

class Crawler:

    def __init__(self, unit):
        self.unit = unit
        self.spiders = [spiders.MainSpider(unit),
                        spiders.ErrorSpider(unit),
                        spiders.AppSpider(unit)]
        self.container = None

    def get_done_work(self):
        return self.container.done()

    def get_total_work(self):
        return self.container.total()

    def crawl(self):

        print('[COMPLEMENT] {0} - {1}'.format(self.unit.url, self.unit.complements))

        self.container = Container(self.unit.url)
        session = requests.Session()
        
        for request in self.container:

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

            time.sleep(1)
            self.unit.sync(self)

        self.unit.sync(self, True)

        return {'status':0}
