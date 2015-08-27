
import re
import urllib
from urllib import parse

from units.http.crawler.container.opac import OPaC


class Container:

    def __init__(self, url):
        self.root = urllib.parse.urljoin(url, './')
        self.seen_urls = {url}
        self.requests = []
        self.filters = set()

        self.opac = OPaC()
        self.opac.add_path(url)

        self.url_pattern = re.compile('^https?://[^?#]+')

    def __iter__(self):
        return self


    def __next__(self):
        if self.requests:
            return self.requests.pop()
        url = parse.urljoin(self.root, next(self.opac))
        return {'method':'get', 'url':url}


    def total(self):
        return (len(self.seen_urls) + len(self.requests))


    def done(self):
        return len(self.seen_urls)


    def add_request(self, request):
        match = self.url_pattern.match(request['url'])
        if not match:
            return

        url = match.group()
        if re.match('^' + self.root, url):

            #for _filter in self.filters:
            #    if _filter.match(url):
            #        return

            if request['method'] == 'get':
                self.opac.add_path(parse.urlparse(url).path)

            elif (request['method'], url) not in self.seen_urls:
                self.seen_urls.add((request['method'], url))
                request['url'] = url
                self.requests.append(request)


    def add_filter(self, _filter):
        _cfilter = re.compile(_filter)
        if _cfilter not in self.filters:
            self.filters.add(_cfilter)
            self.requests = [request for request in self.requests if not _cfilter.match(request['url'])]