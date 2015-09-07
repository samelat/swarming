
import time
import logging
import requests

from modules.dictionary import Dictionary

from units.http.support import Protocol


class BasicAuth(Protocol):

    def __init__(self, unit):
        super().__init__()
        self.unit = unit
        self.logger = logging.getLogger(__name__)
        self.session = requests

    def crack(self, dictionaries):

        result = {'status':0}

        #print('[COMPLEMENT] {0} - {1}'.format(self.unit.url, self.unit.complements))

        request = {'method':'get', 'url':self.unit.url}
        request.update(self.unit.complements)

        for username, password in Dictionary(dictionaries).join():

            self.logger.debug('Trying {0}:{1} over {2}'.format(username, password, self.unit.url))

            request['auth'] = (username, password)

            result, response = self.request(request)
            if result['status'] < 0:
                break

            if response.status_code == 200:
                self.unit.success({'username':username, 'password':password},
                                  {'auth':[username, password]})

        return result