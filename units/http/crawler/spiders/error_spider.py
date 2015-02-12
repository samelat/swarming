
import urllib.parse

class ErrorSpider:

    def __init__(self, crawler):
        self.crawler = crawler

    def parse(self, request, response):

        result = {}

        print('[spider.error] response status_code: {0}'.format(response.status_code))

        if response.status_code in [401]:

            _url = urllib.parse.urlparse(request['url'])

            task = {'resource':{}}
            task['resource'] = {'path': _url.path, 'attrs': {'auth_scheme':'basic'}, 'params': {}}

            task['stage'] = 'forcing.dictionary'

            result['tasks'] = [task]

        return result