
import urllib

from units.http.support import HTML
from units.http.crawler.spiders.spider import Spider


class DefaultSpider(Spider):

    def __init__(self, unit):
        super(DefaultSpider, self).__init__(unit)
        self.tags = {'a':'href', 'frame':'src'}
        self.found_forms = set()

    def parse(self, request, response, extra):

        result = {'requests':[]}

        forms = extra['html'].get_login_forms()
        if forms:

            for form in forms:
                if form['sign'] in self.found_forms:
                    continue

                self.found_forms.add(form['sign'])
                # Create a new Cracking Task over the form we have found.
                crack_task = self.unit.task.copy()
                del(crack_task['id'])
                crack_task['description'] = "General HTML Login Form"

                crack_task.update({'attrs': {'auth_scheme':'post', 'form':{'index':form['index']}},
                                   'path' : urllib.parse.urlparse(response.url).path,
                                   'stage':'cracking.dictionary', 'state':'stopped'})

                self.unit.set_knowledge({'task':crack_task}, block=False)

        tag = extra['html'].find('base')
        base_url = tag.attrs['href'].strip() if tag and tag.has_attr('href') else ''
        base_url = base_url if base_url else response.url

        for name, attr in self.tags.items():
            tags = extra['html'].find_all(name)
            for tag in tags:
                if tag.has_attr(attr):
                    url = urllib.parse.urljoin(base_url, tag.attrs[attr].strip())
                    result['requests'].append({'method':'get', 'url':url})

        return result