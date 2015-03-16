
import os
import re
import json
import urllib.parse

from units.http.crawler.spiders import apps
from units.http.crawler.spiders.spider import Spider

''' ##################################
    General Web Application detection Spider
    ##################################

    If a web application is too complex to be
    molded this wey, you may have to implement
    a Spider to detect it.
'''

class AppSpider(Spider):

    content_types = ['text/html']

    def __init__(self, unit):
        self.unit = unit
        self.apps = self.load_apps('json/apps')


    def load_apps(self, json_path):
        result = {}

        for file_name in os.listdir(json_path):
            try:
                name, extension = file_name.split('.')
            except:
                continue

            if extension != 'json':
                continue

            fd = open(json_path + '/' + file_name, 'r')
            data = fd.read()
            fd.close()

            try:
                result[name] = json.loads(data)
            except ValueError:
                continue

        return result


    def parse(self, request, response, extra):

        result = {'requests':[], 'filters':[], 'dictionaries':[]}

        for app_name, app in self.apps.items():
            # STEP #1
            # First Joomla checking
            if not extra['html'].check(**app['check']):
                continue

            # STEP #2
            # Second Joomla checking and Joomla root path taking
            root_path = extra['html'].get_root_path(**app['path'])
            if not root_path:
                continue

            print('[crawler.spider.app] ES UN JODIDO {0}!!!: {1}'.format(app_name, request['url']))

            # STEP #3
            # Create the filters
            result['filters'] = [urllib.parse.urljoin(response.url, root_path) + '.*']

            # STEP #4
            # Search for the login form. If this page is not Administrator panel, form may not exist.
            login_forms = extra['html'].get_login_forms()

            if not login_forms:
                return result

            # STEP #5
            # Create a new Joomla Cracking Task
            crack_task = self.unit.task.copy()
            del(crack_task['id'])
            crack_task['description'] = app['description']

            crack_task.update({'path': root_path, 'attrs': {'auth_scheme':'post', 'form':{'index':0}},
                               'stage':'cracking.dictionary', 'state':'ready'})

            self.unit.set_knowledge({'task':crack_task}, block=False)

            if 'filters' in result:
                for _filter in result['filters']:
                    if re.match(_filter, request['url']):
                        break

        return result