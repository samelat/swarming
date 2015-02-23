
import re

from units.http.crawler.spiders import apps
from units.http.crawler.spiders.spider import Spider


class AppSpider(Spider):

    content_types = ['text/html']

    def __init__(self, unit):
        self.unit = unit
        self.apps = [apps.Joomla(unit),
                     apps.PHPMyAdmin(unit),
                     apps.Drupal(unit),
                     apps.Moodle(unit),
                     apps.Squirrel(unit),
                     apps.WordPress(unit)]

    def parse(self, request, response, extra):

        results = {'requests':[], 'filters':[], 'dictionaries':[]}

        for app in self.apps:
            result = app.parse(request, response, extra)

            for field, values in result.items():
                results[field].extend(values)

            if 'filters' in result:
                for _filter in result['filters']:
                    if re.match(_filter, request['url']):
                        break

        return results