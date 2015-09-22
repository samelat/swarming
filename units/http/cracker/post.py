
import logging
import requests
from urllib.parse import urlencode

from modules.dictionary import Dictionary

from units.http.support import HTML
from units.http.support import Protocol


class Post(Protocol):

    def __init__(self, unit):
        super().__init__()
        self.unit = unit
        self.logger = logging.getLogger(__name__)

        self.session = None
        self.status_codes = {200:True, 403:False} # OK|FAIL Status Codes


    def crack(self, dictionaries):

        result = {'status': 0}

        attrs = self.unit.task['attrs']

        if 'form' not in attrs:
            return {'status':-3, 'error':'No "form" attribute'}

        cicle = 0
        reload = True
        login_form = None

        for username, password in Dictionary(dictionaries).join():
            self.logger.debug('Trying {0}:{1} over {2}'.format(username, password, self.unit.url))

            if reload:
                cicle = 0
                if self.session:
                    self.session.close()
                self.session = requests.Session()
                
                # Get indexed form
                if 'index' in attrs['form']:
                    # First request to take all info we need to continue.
                    request = {'method':'get', 'url':self.unit.url,
                               'allow_redirects':False}
                    request.update(self.unit.complements)
                    
                    result, response = self.request(request)
                    if result['status'] < 0:
                        break

                    if response.status_code not in self.status_codes:
                        result = {'status':-4, 'error':'Bad Status Code {0}'.format(response.status_code)}
                        break

                    html = HTML(response.text)
                    login_form = html.get_login_forms()[attrs['form']['index']]
                else:
                    login_form = attrs['form']

                request = {'method':'post', 'url':self.unit.url, 'data':{}}
                request.update(self.unit.complements)
                if 'fields' in login_form:
                    request['data'].update(login_form['fields'])

                if not (('usr_field' in login_form) and ('pwd_field' in login_form)):
                    return {'status':-5, 'error':'Incomplete form tag information'}

                reload = False

            request['data'][login_form['usr_field']] = username
            request['data'][login_form['pwd_field']] = password

            result, response = self.request(request)
            if result['status'] < 0:
                break

            if response.status_code not in self.status_codes:
                result = {'status':-4, 'error':'Bad Status Code {0}'.format(response.status_code)}
                break



            html = HTML(response.text)

            # Detect if the login was successful
            if 'fail' in attrs:
                # This will be a complex structure
                pass
            else:
                if self.status_codes[response.status_code] and (login_form not in html):
                    self.unit.success({'username':username, 'password':password},
                                      {'data':request['data']})
                    reload = True
                else:
                    cicle += 1

            if ('attempts' in attrs) and (cicle >= attrs['attempts']):
                reload = True

        if self.session:
            self.session.close()

        return result
