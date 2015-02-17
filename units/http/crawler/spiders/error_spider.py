
import urllib.parse


class ErrorSpider:

    def __init__(self, unit):
        self.unit = unit

    def parse(self, request, response):

        result = {}

        print('[spider.error] response status_code: {0}'.format(response.status_code))

        if response.status_code in [401]:

            _url = urllib.parse.urlparse(request['url'])

            resource = self.unit.resource.copy()
            del(resource['id'])
            resource.update({'path': _url.path, 'attrs': {'auth_scheme':'basic'}})
            response = self.unit.set_knowledge({'task':{'stage':'forcing.dictionary', 'resource':resource}})

            print('[http.crawling] RESPONSE: {0}'.format(response))

            if response['status'] == 0:
                resource = self.unit.resource.copy()
                del(resource['id'])
                resource.update({'path': _url.path, 'dependence':{'id':response['values']['task']['resource']['id']}})
                self.unit.set_knowledge({'task':{'stage':'waiting.dependence.crawling', 'resource':resource}}, block=False)

            result['filters'] = [urllib.parse.urljoin(request['url'], '.*')]

        return result