
import requests
from urllib.parse import urlencode

from units.http.tools import HTML
from modules.dictionary import Dictionary


class Post:

    def __init__(self, unit):
        self.unit = unit

    def crack(self, dictionaries):

        print('[<#########>] {0}'.format(self.unit.task))

        print('[COMPLEMENT] {0} - {1}'.format(self.unit.url, self.unit.complements))

        attrs = self.unit.task['attrs']

        if 'form' not in attrs:
            return {'status':-1, 'msg':'No "form" attribute'}

        cicle = 0
        reload = True
        session = None
        login_form = None

        try:
            for username, password in Dictionary(dictionaries).join():
                print('[http] Forcing Username: {0} - Password: {1}'.format(username, password))

                if reload:
                    cicle = 0
                    if session:
                        session.close()
                    session = requests.Session()
                    
                    # Get indexed form
                    if 'index' in attrs['form']:
                        # First request to take all info we need to continue.
                        request = {'method':'get', 'url':self.unit.url,
                                   'allow_redirects':False}
                        request.update(self.unit.complements)
                        
                        response = session.request(**request)

                        html = HTML(response.text)
                        login_form = html.get_login_forms()[attrs['form']['index']]
                    else:
                        login_form = attrs['form']

                    request = {'method':'post', 'url':self.unit.url, 'data':{}}
                    request.update(self.unit.complements)
                    if 'fields' in login_form:
                        request['data'].update(login_form['fields'])

                    if not (('usr_field' in login_form) and ('pwd_field' in login_form)):
                        return {'status':-2, 'msg':'Incomplete form tag information'}

                    reload = False

                request['data'][login_form['usr_field']] = username
                request['data'][login_form['pwd_field']] = password

                response = session.request(**request)
                html = HTML(response.text)

                # Detect if the login was successful
                if 'fail' in attrs:
                    # This will be a complex structure
                    pass
                else:
                    if login_form not in html:
                        self.unit.success({'username':username, 'password':password},
                                          {'data':request['data']})
                        reload = True
                    else:
                        cicle += 1

                print('()()()() CICLE == {0} ()()()()'.format(cicle))
                if ('attempts' in attrs) and (cicle >= attrs['attempts']):
                    print('[][][][] REINICIO!!! [][][][]')
                    reload = True
        except requests.exceptions.ConnectionError:
            return {'status':-1, 'error':'Connection Error'}

        if session:
            session.close()

        return {'status':0}