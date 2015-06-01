
import re
import urllib.parse

from units.http.crawler.spiders.spider import Spider


class ErrorSpider(Spider):

    status_codes = [301, 302, 401, 407]

    def __init__(self, unit):
        self.unit = unit


    def parse(self, request, response, extra):

        result = {}

        print('[spider.error] response status_code: {0}'.format(response.status_code))

        # Moved Permanently
        if response.status_code == 301:
            if re.search('^' + re.escape(request['url']), response.headers['location']):
                new_request = request.copy()
                new_request['url'] = response.headers['location']
                result['requests'] = [new_request]

        # www-Authentication
        elif response.status_code == 401:

            _url = urllib.parse.urlparse(request['url'])

            crack_task = self.unit.task.copy()
            del(crack_task['id'])
            crack_task.update({'path': _url.path, 'attrs': {'auth_scheme':'basic'},
                               'stage':'cracking.dictionary', 'state':'ready',
                               'description':'HTTP Basic Auth'})

            crawl_task = self.unit.task.copy()
            del(crawl_task['id'])
            crawl_task.update({'path': _url.path, 'dependence':crack_task,
                               'stage':'waiting.dependence.crawling', 'state':'ready'})

            self.unit.set_knowledge({'task':crawl_task}, block=False)

            result['filters'] = [urllib.parse.urljoin(request['url'], '.*')]

            result['break'] = True

        # Proxy Authentication
        elif response.status_code == 407:
            pass

        return result