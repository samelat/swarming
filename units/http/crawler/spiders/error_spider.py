
import re
from urllib import parse

from units.http.crawler.spiders.spider import Spider


class ErrorSpider(Spider):

    status_codes = [301, 302, 401, 407]
    content_types = []

    def __init__(self, unit):
        super(ErrorSpider, self).__init__(unit)
        self.status_data = {
            401 : set()
        }


    def parse(self, request, response, content):

        result = {}

        #print('[spider.error] response status_code: {0}'.format(response.status_code))

        # Moved Permanently
        # Redirection
        if response.status_code in [301, 302]:
            print('[!] Error 301')
            redirection = parse.urljoin(request['url'], response.headers['location'])
            new_request = request.copy()
            new_request['url'] = redirection
            result['requests'] = [new_request]
            print('[!] Nuevo request: {0}'.format(new_request))

        # www-Authentication
        elif response.status_code == 401:

            header = response.headers['www-authenticate']
            scheme = re.match('(?P<auth>\w+)\srealm\=\"(?P<realm>[^\"]+)\"', header).groupdict()
            if scheme['realm'] not in self.status_data[401]:

                self.status_data[401].add(scheme['realm'])

                url = parse.urlparse(parse.urljoin(request['url'], './'))

                crack_task = self.unit.task.copy()
                del(crack_task['id'])
                crack_task.update({'path': url.path, 'attrs': {'auth_scheme':scheme['auth'].lower()},
                                   'stage':'cracking.dictionary', 'state':'ready',
                                   'description':'HTTP {0} Auth'.format(scheme['auth'])})

                crawl_task = self.unit.task.copy()
                del(crawl_task['id'])
                crawl_task.update({'path': url.path, 'dependence':crack_task,
                                   'stage':'waiting.dependence.crawling', 'state':'ready'})

                self.unit.set_knowledge({'task':crawl_task}, block=False)

                result['filters'] = [parse.urljoin(request['url'], '.*')]

        # Not Found
        elif response.status_code == 404:
            # TODO: We sould make a kind of page sign to identify
            # which pages we have visited.
            result = self.unit.spiders['default'].parse(request, response, content)

        # Proxy Authentication
        elif response.status_code == 407:
            pass

        return result