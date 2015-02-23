
import re
import urllib.parse

from units.http.crawler.spiders.spider import Spider


class Moodle(Spider):

    content_types = ['text/html']

    def parse(self, request, response, extra):

        result = {}

        # <meta name="keywords" content="moodle, ...
        if extra['bs'].find_all('meta', attrs={'name':'keywords'}, content=re.compile('^moodle, ')):

            print('[crawler.spider.app] ES UN JODIDO MOODLE!!!: {0}'.format(request['url']))
            result['filters'] = [urllib.parse.urljoin(response.url, '.*')]

        return result