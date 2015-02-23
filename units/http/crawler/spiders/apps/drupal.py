
import re
import urllib.parse

from units.http.crawler.spiders.spider import Spider


class Drupal(Spider):

    content_types = ['text/html']

    def parse(self, request, response, extra):

        result = {}

        # <link rel="stylesheet" type="text/css" href="phpmyadmin.css.php?serv
        if extra['bs'].find_all('script', attrs={'type':'text/javascript'}, 
                                          src=re.compile('/misc/drupal.js')):

            print('[crawler.spider.app] ES UN JODIDO DRUPAL!!!: {0}'.format(request['url']))
            result['filters'] = [urllib.parse.urljoin(response.url, '.*')]

        return result