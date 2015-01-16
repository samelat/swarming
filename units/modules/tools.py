
import random


def new_msg(dst, cmd, params={}):
    message = {'dst':dst,
               'cmd':cmd,
               'params' : params.copy()}
    return message

def make_response(message):
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

def gen_token():
    return random.getrandbits(32)

''' This method control if the message has all the things
    it should have.
'''
def check_msg(message):
    if not 'id' in message:
        message['id'] = gen_token()

    if not 'dst' in message:
        return False

    return True

def restrict(message, keys):
    return dict([(key, message[key]) for key in keys if key in message])

def msg_to_str(message):
    channel = -1
    if 'channel' in message:
        channel = message['channel']
    return 'dst: {0} - src: {1} - cmd: {2} - channel: {3}'.format(message['dst'],
                                                                  message['src'],
                                                                  message['cmd'],
                                                                  channel)
