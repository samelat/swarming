
import re
import urllib.parse

from units.http.crawler.spiders.spider import Spider


class Joomla(Spider):

    content_types = ['text/html']

    def parse(self, request, response, extra):

        result = {}

        if extra['bs'].find_all('meta', attrs={'name':'generator'}, content=re.compile('^Joomla! ')):

            print('[crawler.spider.app] ES UN JODIDO JOOMLA!!!: {0}'.format(request['url']))
            result['filters'] = [urllib.parse.urljoin(response.url, '.*')]

            crack_task = self.unit.task.copy()
            del(crack_task['id'])
            crack_task.update({'path': _url.path, 'attrs': {'auth_scheme':'post'},
                               'stage':'forcing.dictionary', 'state':'ready'})

            self.unit.set_knowledge({'task':crawl_task}, block=False)

        return result