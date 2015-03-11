
import re
import urllib.parse

from units.http.crawler.spiders.spider import Spider


class Joomla(Spider):

    content_types = ['text/html']

    def parse(self, request, response, extra):

        result = {}

        # First Joomla checking
        if not extra['bs'].find_all('meta', attrs={'name':'generator'}, content=re.compile('^Joomla! ')):
            return result

        # Second Joomla checking and Joomla root path taking
        joomla_root = None
        scripts = extra['bs'].find_all('script', attrs={'type':'text/javascript', 'src':True})

        for script in scripts:
            matches = re.findall('(.+)media/system/js/', scripts.attrs['src'])
            if matches:
                joomla_root = matches[0]
                break

        if not joomla_root:
            return result

        print('[crawler.spider.app] ES UN JODIDO JOOMLA!!!: {0}'.format(request['url']))

        # Create the filters
        result['filters'] = [urllib.parse.urljoin(response.url, joomla_root) + '.*']

        # Search for the login form. If this page is the main one, form may not exist.
        form_index = 0
        forms = extra['bs'].find_all('script', attrs={'type':'text/javascript', 'src':True})
        for form in forms:
            if form.find('input', attrs={'type':'password'}) and\
               form.find('input', attrs={'type':'text'})):
                break
            form_index += 1

        if form_index == len(forms):
            return result

        # Create the new Joomla Cracking Task
        crack_task = self.unit.task.copy()
        del(crack_task['id'])

        attrs = {'auth_scheme':'post',
                 'form':{'index':form_index}}

        crack_task.update({'path': joomla_root, 'attrs': attrs,
                           'stage':'cracking.dictionary', 'state':'ready'})

        self.unit.set_knowledge({'task':crawl_task}, block=False)

        return result