
import re
import urllib

class Container:

    def __init__(self, url):
        self.root = url
        self.urls = {url}
        self.requests = [{'method':'get', 'url':url}]
        self.filters = set()

    def __iter__(self):
        return self


    def __next__(self):
        try:
            return self.requests.pop()
        except:
            raise StopIteration


    def add_request(self, request):
        url = urllib.parse.urljoin(self.root, request['url'])

        if re.match(self.root, url):
            request['url'] = url
            self.urls.add(url)
            self.requests.append(request)

    def add_filter(self, _filter):
        _cfilter = re.compile(_filter)
        if not _cfilter in self.filters:
            self.filters.add(_cfilter)
            self.requests = [request for request in self.requests if not re.match(_cfilter, request['url'])]