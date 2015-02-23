
import re
import urllib.parse

from units.http.crawler.spiders.spider import Spider


class Squirrel(Spider):

    content_types = ['text/html']

    def parse(self, request, response, extra):

        result = {}

        # <body ... onLoad="squirrelmail_loginpage_onload();">
        if extra['bs'].find_all('body', onload=re.compile('^squirrelmail\_')):

            print('[crawler.spider.app] ES UN JODIDO SQUIRREL!!!: {0}'.format(request['url']))
            result['filters'] = [urllib.parse.urljoin(response.url, '.*')]

        return result