
import re
import urllib.parse

from units.http.crawler.spiders.spider import Spider


class WordPress(Spider):

    content_types = ['text/html']

    def parse(self, request, response, extra):

        result = {}

        # <meta content="WordPress 3.6" name="generator"/>
        # First App checking
        if not extra['bs'].find_all('meta', attrs={'name':'generator'}, 
                                        content=re.compile('^WordPress ')):
            return result

        # Second checking and App root path taking
        root = None
        scripts = extra['bs'].find_all('script', attrs={'type':'text/javascript', 'src':True})

        for script in scripts:
            matches = re.findall('(.+)media/system/js/', script.attrs['src'])
            if matches:
                root = matches[0]
                break

        if not root:
            return result

        print('[crawler.spider.app] ES UN JODIDO WORDPRESS!!!: {0}'.format(request['url']))
        result['filters'] = [urllib.parse.urljoin(response.url, '.*')]

        return result