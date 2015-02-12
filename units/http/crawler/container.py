
import re
import urllib

class Container:

    def __init__(self, url):
        self.root = url
        self.urls = {url}
        self.requests = [{'method':'get', 'url':url}]

    def __iter__(self):
        return self


    def __next__(self):
        try:
            return self.requests.pop()
        except:
            raise StopIteration


    def add(self, request):
        url = urllib.parse.urljoin(self.root, request['url'])

        if re.match(self.root, url):
            request['url'] = url
            self.urls.add(url)
            self.requests.append(request)