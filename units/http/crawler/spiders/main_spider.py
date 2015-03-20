
import urllib

from units.http.crawler.spiders.spider import Spider


class MainSpider(Spider):

    def __init__(self, unit):
        self.unit = unit

    def parse(self, request, response, extra):

        result = {'requests':[]}

        a_tags = extra['html'].find_all('a')
        for tag in a_tags:
            if tag.has_attr('href'):
                url = urllib.parse.urljoin(response.url, tag.attrs['href'])
                result['requests'].append({'method':'get', 'url':url})

        return result