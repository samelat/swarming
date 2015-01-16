''' This module simplify messages manipulation
'''
import random

class Message:

    def __init__(self, message={}):
        self.message = message

        message = {'dst':dst,
                   'cmd':cmd,
                   'params' : params.copy()}


    def __str__(self):
        result = 'dst: {0}'.format(message['dst'])

        result += ' - src: {0}'.format(message['src'])
        result += ' - cmd: {0}'.format(meesage['cmd'])

        if 'channel' in self.message:
            result += ' - channel: {0}'.format(self.message['channel'])

        return result


    def gen_token(self):
        return random.getrandbits(32)


    def response(self):
        if (message['cmd'] == 'response') or\
            not(('src' in message) and ('channel' in message)):
            return None

        response = {}
        response['channel']  = message['channel']
        response['src'] = message['dst']
        response['cmd'] = 'response'
        response['params'] = {}
        
        response['dst'] = message['src']

        return response


    ''' This method control if the message has all the things
        it should have.
    '''
    def check(self):
        if not 'id' in message:
            message['id'] = gen_token()

        if not 'dst' in message:
            return False

        return True

    # ?????
    #def restrict(self, keys):
    #    return dict([(key, message[key]) for key in keys if key in message])
