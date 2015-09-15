
import re
import urllib
from urllib import parse

from units.http.crawler.container.opac import OPaC


class Container:

    def __init__(self, first_request):
        self.roots = {}
        self.requests = [first_request]
        self.seen_requests = set()
        self.done_counter = 0
        self.filters = set()

        #self.opac_done = 0
        #self.opac = {'http':OPaC(), 'https':OPaC()
        #self.opac.add_path(url)

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
                return {'method':'get', 'url':url}
        raise StopIteration


    def total(self):
        roots_len = sum([len(root) for root in self.roots.values()])
        return self.done_counter + roots_len + len(self.requests)


    def done(self):
        return self.done_counter


    def add_request(self, request):
        try:
            url = re.match('^https?://[^?#]+', request['url']).group()
            request_root = parse.urljoin(url, './')

            for root in self.roots:
                # if "http://example.com/" is root of "http://example.com/chori/" (the request_root)
                if re.match('^' + root, request_root):
                    request_root = root
                    break

                # if "http://example.com/chori/" (request_root) is root of "http://example.com/chori/pan/"
                # This could happen because we don't know when a less deep root could appear.
                if re.match('^' + request_root, root):
                    self.roots[request_root] = self.roots[root]
                    del(self.roots[root])
                    break

            if request_root not in self.roots:
                self.roots[request_root] = OPaC()

            if request['method'] == 'get':
                request['url'] = url
                self.roots[request_root].add_path(parse.urlparse(url).path)

            elif (request['method'], url) not in self.done_requests:
                self.done_requests.add((request['method'], url))
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