
import random


def new_msg(dst, cmd, params={}):
    message = {'dst':dst,
               'cmd':cmd,
               'id' :gen_token(),
               'params' : params.copy()}
    return message

def make_response(message):
    response = message.copy()
    response['src'] = message['dst']
    response['cmd'] = 'response'

    if 'src' in message:
        response['dst'] = message['src']

    return response

def gen_token():
    return random.getrandbits(32)

''' This method control if the message have all the things
    that it should have.
'''
def check_msg(message):
    if not 'id' in message:
        message['id'] = gen_token()

    if not 'dst' in message:
        return False

    return True

def restrict(message, keys):
    return dict([(key, message[key]) for key in keys if key in message])

