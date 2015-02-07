''' This module simplify messages manipulation
'''
import random

class Message:

    def __init__(self, message={}):
        self.raw = message.copy()

        for field in ['cmd', 'dst', 'src']:
            if not field in self.raw:
                raise ValueError


    def __str__(self):

        conn_info = ''
        if 'layer' in self.raw:
            conn_info += 'layer:{0}'.format(self.raw['layer'])

        if 'channel' in self.raw:
            if conn_info:
                conn_info += '|'
            conn_info += 'channel:{0}'.format(self.raw['channel'])

        if 'jump' in self.raw:
            if conn_info:
                conn_info += '|'
            conn_info += 'jump:{0}'.format(self.raw['jump'])

        return '[{src}]-----[{0}]--({cmd}|{params})----->[{dst}]'.format(conn_info, **self.raw)


    def add_channel(self):
        if not 'channel' in  self.raw:
            self.raw['channel'] = random.getrandbits(32)


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
    
