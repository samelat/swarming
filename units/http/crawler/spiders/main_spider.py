
from units.http.crawler.spiders.spider import Spider


class MainSpider(Spider):

    content_types = ['text/html']

    def __init__(self, unit):
        self.unit = unit

    def parse(self, request, response, extra):

        result = {'requests':[]}

        a_tags = extra['bs'].find_all('a')
        for tag in a_tags:
            if tag.has_attr('href'):
                result['requests'].append({'method':'get', 'url':tag.attrs['href']})

        return result