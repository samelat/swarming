
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode

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
        fields = {}
        usr_field = None
        pwd_field = None
        if 'index' in attrs['form']:
            if not response:
                response = requester.request(method='get', url=self.unit.url)
            bs = BeautifulSoup(response.text)

            form = bs.find_all('form')[attrs['form']['index']]
            map(lambda i: i.attrs)
            inputs = [inp in form.find_all('input', {'name':True}) if ]
            fields = [() for inp in form.find_all('input', {'name':True})]

            for _input in inputs:
                if 'type' not in _input.attrs:
                    _input.attrs['type'] == 'text'
                try:
                    if (_input.attrs['type'] == 'text') and not (('value' in _input.attrs) and _input.attrs['value']):
                        usr_field = _input.attrs['name']

                    elif (_input.attrs['type'] == 'password') and not (('value' in _input.attrs) and _input.attrs['value']):
                        pwd_field = _input.attrs['name']

                    elif _input.attrs['type'] == 'hidden':
                        fields[_input.attrs['name']] = _input.attrs['value']

                except:
                    continue

        print('[cracking.attrs] {0}'.format(attrs))

        if 'usr_field' in attrs['form']:
            usr_field = attrs['usr_field']

        if 'pwd_field' in attrs['form']:
            pwd_field = attrs['pwd_field']

        if not (usr_field and pwd_field):
            return {'status':-2, 'msg':'Incomplete form tag information'}

        # Update data fields
        if 'fields' in attrs['form']:
            fields.update(attrs['form']['fields'])

        # Start cracking
        request['data'] = fields
        for dictionary in dictionaries:
            for username, password in Dictionary(**dictionary).pairs():
                print('[http] Forcing Username: {0} - Password: {1}'.format(username, password))

                request['data'][usr_field] = username
                request['data'][pwd_field] = password

                response = requester.request(**request)

                # Detect if the login was successful
                bs = BeautifulSoup(response.text)

                success = False
                if 'fail' in attrs:
                    pass
                else:
                    try:
                        form = bs.find_all('form')[0]

                        inputs = form.find_all('input', attrs={'name':usr_field})
                        inputs.extend(form.find_all('input', attrs={'name':pwd_field}))

                        if len(inputs) < 2:
                            success = True

                    except IndexError:
                        success = True

                if success:
                    self.unit.success({'username':username, 'password':password},
                                      {})

                if ('update' in attrs['form']) and attrs['form']['update']:
                    pass

        return {'status':0}