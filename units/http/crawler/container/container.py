
import re
from urllib import parse

from units.http.crawler.container.opac import OPaC


class Container:

    def __init__(self, first_request, limit=False):
        self.roots = {}
        self.requests = [first_request]
        self.done_requests = set()
        self.done_counter = 0
        self.filters = set()
        self.limit = limit

        if self.limit:
            request_root = parse.urljoin(first_request['url'], './')
            self.roots[request_root] = OPaC()

    def __iter__(self):
        return self

    def __next__(self):
        if self.requests:
            self.done_counter += 1
            return self.requests.pop()

        for root, opac in self.roots.items():
            if len(opac):
                url = parse.urljoin(root, next(opac))
                self.done_counter += 1
                return {'method': 'get', 'url': url}
        raise StopIteration

    def total(self):
        roots_len = sum([len(root) for root in self.roots.values()])
        return self.done_counter + roots_len + len(self.requests)

    def done(self):
        return self.done_counter

    def add_request(self, request):
        try:
            request_root = None
            for root in self.roots:
                if re.match('^' + root, request['url']):
                    request_root = root
                    break

            if not request_root:
                if self.limit:
                    return False
                request_root = parse.urljoin(request['url'], '/')
                self.roots[request_root] = OPaC()

            if request['method'] == 'get':
                self.roots[request_root].add_path(parse.urlparse(request['url']).path)

            elif (request['method'], request['url']) not in self.done_requests:
                self.done_requests.add((request['method'], request['url']))
                self.requests.append(request)

        except Exception as e:
            print(e)
            return False

        return True


    def add_filter(self, _filter):
        _cfilter = re.compile(_filter)
        if _cfilter not in self.filters:
            self.filters.add(_cfilter)
            self.requests = [request for request in self.requests if not _cfilter.match(request['url'])]