
import urllib
import requests

from units.http.crawler.container import Container
from units.http.crawler import spiders

class Crawler:

    def __init__(self, unit):
        self.unit = unit
        self.spiders = [spiders.BasicSpider(self),
                        spiders.ErrorSpider(self)]
        self.container = None

        self.resource = None

    def crawl(self, resource):

        '''
{'path': '/', 'attrs': {}, 'id': 2, 'params': {}, 'service': {'protocol': {'name': 'http', 'id': 1}, 'id': 1, 'hostname': '127.0.0.1', 'port': 80}}
        '''
        
        self.resource = resource

        url = urllib.parse.urlunparse((resource['service']['protocol']['name'],
                                       '{0}:{1}'.format(resource['service']['hostname'], resource['service']['port']),
                                       resource['path'],
                                       '',
                                       '',
                                       ''))

        self.container = Container(url)
        
        for request in self.container:

            if not 'allow_redirects':
                request['allow_redirects'] = False

            try:
                response = requests.request(**request)
            except:
                print('[crawler] Error requesting {0}'.format(request))

            for spider in self.spiders:
                result = spider.parse(request, response)

                if 'requests' in result:
                    for _request in result['requests']:
                        self.container.add(_request)

                if 'dictionaries' in result:
                    for dictionary in result['dictionaries']:
                        print('[http.crawler] new dictionary: {0}'.format(dictionary))

                if 'tasks' in result:
                    for task in result['tasks']:
                        if 'service' not in task['resource']:
                            task['resource']['service'] = {}
                            task['resource']['service']['id'] = resource['service']['id']

                        self.unit.set_knowledge({'task':task})

        return {'status':0}
