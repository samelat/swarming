
import requests

from modules.dictionary import Dictionary


class Post:

    def __init__(self, unit):
        self.unit = unit

    def crack(self, dictionaries):

        print('[<#########>] {0}'.format(self.unit.task))

        attrs = self.unit.task['attrs']

        request = {'method':'POST', 'url':self.unit.url}
        request.update(self.unit.complements)

        response = None
        if ('session' in attrs) and not attrs['session']:
            requester = requests
        else:
            requester = requests.Session()
            response = requester.request(method='get', url=self.unit.url)

        if 'form' not in attrs:
            return {'status':-1, 'msg':'No "form" attribute'}

        # Getting indexed form
        data = {}
        if 'index' in attrs['form']:
            if not response:
                response = requester.request(method='get', url=self.unit.url)
            bs = BeautifulSoup(response.text)

            form = bs.find_all('form')[attrs['form']['index']]
            inputs = form.find_all('input')

            

        if 'fields' in attrs['form']:
            data.update(attrs['form']['fields'])

        for dictionary in dictionaries:
            for username, password in Dictionary(**dictionary).pairs():
                print('[http] Forcing Username: {0} - Password: {1}'.format(username, password))

                response = requester.request(**request)

                if ('update' in attrs['form']) and attrs['form']['update']:
                    pass


        time.sleep(5)

        return {'status':0}