
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

    def crawl(self, task):

        '''
        'resource': {'protocol': 'http', 'id': 1, 'port': 8090, 'path': '/joomla/', 'attrs': {}, 'hostname': '192.168.2.3'}
        '''
        
        self.resource = task['resource']

        url = '{protocol}://{hostname}:{port}{path}'.format(**self.resource)
        if 'query' in self.resource['attrs']:
            url += self.resource['attrs']['query']

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
                    for _task in result['tasks']:
                        _resource = self.resource.copy()
                        del(_resource['id'])
                        if 'resource' in _task:
                            _resource.update(_task['resource'])
                        _task['resource'] = _resource
                        self.unit.set_knowledge({'task':_task})

        self.unit.set_knowledge({'task':{'id':task['id'], 'stage':'complete'}})

        return {'status':0}
