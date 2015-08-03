
import time
import requests

from modules.dictionary import Dictionary


class BasicAuth:

    def __init__(self, unit):
        self.unit = unit

    def crack(self, dictionaries):

        #print('[COMPLEMENT] {0} - {1}'.format(self.unit.url, self.unit.complements))

        request = {'method':'get', 'url':self.unit.url}
        request.update(self.unit.complements)

        for username, password in Dictionary(dictionaries).join():
            #print('[http] Forcing Username: {0} - Password: {1}'.format(username, password))
            request['auth'] = (username, password)

            try:
                response = requests.request(**request)
            except requests.exceptions.ConnectionError:
                return {'status':-1, 'error':'Connection Error'}

            if response.status_code == 200:
                self.unit.success({'username':username, 'password':password},
                                  {'auth':[username, password]})

        return {'status':0}