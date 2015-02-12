
from bs4 import BeautifulSoup


class BasicSpider:

    def __init__(self, crawler):
        self.crawler = crawler

    def parse(self, request, response):

        print('[spider.basic] response: {0}'.format(response.headers))

        return {}