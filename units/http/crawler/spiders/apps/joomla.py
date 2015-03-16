
import re

from units.http.crawler.spiders.spider import Spider


class Joomla(Spider):

    content_types = ['text/html']

    def parse(self, request, response, extra):

        result = {}

        # STEP #1
        # First Joomla checking
        if not extra['html'].check('meta', attrs={'name':'generator'},
                                              content=re.compile('^Joomla! ')):
            return result

        # STEP #2
        # Second Joomla checking and Joomla root path taking

        joomla_root = extra['html'].get_root_path({'name':'script', 'attrs':{'type':'text/javascript'}},
                                                  'src', '(.+)media/system/js/')
        if not joomla_root:
            return result

        print('[crawler.spider.app] ES UN JODIDO JOOMLA!!!: {0}'.format(request['url']))

        # STEP #3
        # Create the filters
        result['filters'] = [urllib.parse.urljoin(response.url, joomla_root) + '.*']

        # STEP #4
        # Search for the login form. If this page is not Administrator panel, form may not exist.
        login_forms = extra['html'].get_login_forms()

        if not login_forms:
            return result

        # STEP #5
        # Create a new Joomla Cracking Task
        crack_task = self.unit.task.copy()
        del(crack_task['id'])
        crack_task['description'] = 'Joomla! Client Form'

        attrs = {'auth_scheme':'post',
                 'form':{'index':form_index}}

        crack_task.update({'path': joomla_root, 'attrs': attrs,
                           'stage':'cracking.dictionary', 'state':'ready'})

        self.unit.set_knowledge({'task':crack_task}, block=False)

        return result