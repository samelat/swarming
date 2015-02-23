
import re
import urllib.parse

from units.http.crawler.spiders.spider import Spider


class WordPress(Spider):

    content_types = ['text/html']

    def parse(self, request, response, extra):

        result = {}

        # <meta content="WordPress 3.6" name="generator"/>
        if extra['bs'].find_all('meta', attrs={'name':'generator'}, 
                                        content=re.compile('^WordPress ')):

            print('[crawler.spider.app] ES UN JODIDO WORDPRESS!!!: {0}'.format(request['url']))
            result['filters'] = [urllib.parse.urljoin(response.url, '.*')]

        return result