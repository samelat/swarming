
import urllib

from units.http.tools import HTML
from units.http.crawler.spiders.spider import Spider


class DefaultSpider(Spider):

    def __init__(self, unit):
        self.unit = unit
        self.tags = {'a':'href', 'frame':'src'}

    def parse(self, request, response, extra):

        result = {'requests':[]}

        forms = extra['html'].get_login_forms()
        if forms:
            # Create a new Cracking Task over the form we have found.
            crack_task = self.unit.task.copy()
            del(crack_task['id'])
            crack_task['description'] = "General HTML Login Form"

            crack_task.update({'attrs': {'auth_scheme':'post', 'form':{'index':0}},
                               'path' : urllib.parse.urlparse(response.url).path,
                               'stage':'cracking.dictionary', 'state':'ready'})

            self.unit.set_knowledge({'task':crack_task}, block=False)

        for name, attr in self.tags.items():
            tags = extra['html'].find_all(name)
            for tag in tags:
                if tag.has_attr(attr):
                    url = urllib.parse.urljoin(response.url, tag.attrs[attr])
                    result['requests'].append({'method':'get', 'url':url})

        return result