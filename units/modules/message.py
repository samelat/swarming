''' This module simplify messages manipulation
'''
import random

class Message:

    def __init__(self, message={}):
        self.raw = message.copy()

        if 'channel' not in self.raw:
            self.raw['channel'] = self.new_token()

        for field in ['cmd', 'dst', 'src']:
            if not field in self.raw:
                raise ValueError


    def __str__(self):
        result = 'dst: {0}'.format(self.raw['dst'])

        result += ' - src: {0}'.format(self.raw['src'])
        result += ' - cmd: {0}'.format(self.meesage['cmd'])

        if 'channel' in self.raw:
            result += ' - channel: {0}'.format(self.raw['channel'])

        return result


    def new_token(self):
        return random.getrandbits(32)


    def make_response(self, values):
        if (self.raw['cmd'] == 'response'):
            return None

        try:
            response = {}
            response['src'] = self.raw['dst']
            response['dst'] = self.raw['src']
            response['layer'] = self.raw['layer']
            response['channel'] = self.raw['channel']
            response['cmd'] = 'response'
            response['params'] = values.copy()
        except KeyError:
            return None

        return response
    
