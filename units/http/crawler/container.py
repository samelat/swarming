
import re
import urllib

class Container:

    def __init__(self, url):
        self.root = urllib.parse.urljoin(url, '/')
        self.seen_urls = {url}
        self.requests = [{'method':'get', 'url':url}]
        self.filters = set()

        self.filter = re.compile('\w+://[^?#]+')

    def __iter__(self):
        return self


    def __next__(self):
        try:
            request = self.requests.pop()
            return request
        except IndexError:
            raise StopIteration


    def total(self):
        return (len(self.seen_urls) - len(self.requests))


    def done(self):
        return len(self.seen_urls)


    def add_request(self, request):
        match = self.filter.match(request['url'])
        if not match:
            return

        url = match.group()
        if re.match(self.root, url) and (url not in self.seen_urls):

            for _filter in self.filters:
                if _filter.match(url):
                    return

            self.seen_urls.add(url)

            request['url'] = url
            self.requests.append(request)


    def add_filter(self, _filter):
        _cfilter = re.compile(_filter)
        if _cfilter not in self.filters:
            self.filters.add(_cfilter)
            self.requests = [request for request in self.requests if not _cfilter.match(request['url'])]