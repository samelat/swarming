
import re
import urllib
from bs4 import BeautifulSoup


class HTML(BeautifulSoup):

    def __contains__(self, login_form):
        # Maybe we sould control action field too
        for form in self.find_all('form'):
            if form.find('input', attrs={'name':login_form['usr_field']}) and\
               form.find('input', attrs={'name':login_form['pwd_field']}):
                return True
        return False


    def get_css_sign(self, tag):
        css_sign = []

        parent = tag
        while parent:
            attrs = parent.attrs
            if ('id' in attrs) and attrs['id']:
                css_sign.append(('id', attrs['id']))
            else:
                css_sign.append(('name', parent.name))

        return tuple(css_sign)


    def get_login_forms(self):
        results = []

        forms = self.find_all('form')
        for form in forms:
            for inp in form.find_all('input', {'type':False}):
                inp.attrs['type'] = 'text'

            txt_fields = form.find_all('input', attrs={'name':True, 'type':'text'})
            pwd_fields = form.find_all('input', attrs={'name':True, 'type':'password'})

            if (len(txt_fields) != 1) or (len(pwd_fields) != 1):
                continue

            usr_field = txt_fields[0]
            pwd_field = pwd_fields[0]

            json_form = {'usr_field':usr_field.attrs['name'],
                         'pwd_field':pwd_field.attrs['name'],
                         'fields':{},
                         'sign':self.get_css_sign(form)}

            for inp in form.find_all('input', attrs={'name':True, 'value':True}):
                json_form['fields'][inp.attrs['name']] = inp.attrs['value']

            results.append(json_form)
            json_form['index'] = len(results) - 1

        return results

    def check(self, tag, attr, regex):
        if attr not in tag['attrs']:
            tag['attrs'][attr] = re.compile(regex)

        return bool(self.find(**tag))


    # Tag Format Example: {'name':'script', 'attrs':{'type':'text/javascript'}}
    def get_root_path(self, tag, attr, regex):
        if attr not in tag['attrs']:
            tag['attrs'][attr] = re.compile(regex)

        bs_tag = self.find(**tag)
        if bs_tag:
            return urllib.parse.urlparse(tag['attrs'][attr].findall(bs_tag.attrs[attr])[0]).path
        return None

