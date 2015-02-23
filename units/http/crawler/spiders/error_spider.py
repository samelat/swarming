
import urllib.parse

from units.http.crawler.spiders.spider import Spider


class ErrorSpider(Spider):

    def __init__(self, unit):
        self.unit = unit


    def accept(self, response, extra):
        return True


    def parse(self, request, response, extra):

        result = {}

        print('[spider.error] response status_code: {0}'.format(response.status_code))

        # www-Authentication
        if response.status_code == 401:

            _url = urllib.parse.urlparse(request['url'])

            crack_task = self.unit.task.copy()
            del(crack_task['id'])
            crack_task.update({'path': _url.path, 'attrs': {'auth_scheme':'basic'},
                               'stage':'forcing.dictionary', 'state':'ready'})

            crawl_task = self.unit.task.copy()
            del(crawl_task['id'])
            crawl_task.update({'path': _url.path, 'dependence':crack_task,
                               'stage':'waiting.dependence.crawling', 'state':'ready'})

            self.unit.set_knowledge({'task':crawl_task}, block=False)

            result['filters'] = [urllib.parse.urljoin(request['url'], '.*')]

        # Proxy Authentication
        elif response.status_code == 407:
            pass

        return result