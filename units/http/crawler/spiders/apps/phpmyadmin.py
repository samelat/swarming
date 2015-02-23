
import re
import urllib.parse

from units.http.crawler.spiders.spider import Spider


class PHPMyAdmin(Spider):

    content_types = ['text/html']

    def parse(self, request, response, extra):

        result = {}

        # <link rel="stylesheet" type="text/css" href="phpmyadmin.css.php?serv
        if extra['bs'].find_all('link', attrs={'rel':'stylesheet'}, 
                                        href=re.compile('^phpmyadmin\.css\.php')):

            print('[crawler.spider.app] ES UN JODIDO PHPMYADMIN!!!: {0}'.format(request['url']))
            result['filters'] = [urllib.parse.urljoin(response.url, '.*')]

        return result