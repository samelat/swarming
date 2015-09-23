
import logging
from threading import Condition

from common.message import Message


class Unit:

    light = False
    protocols = []

    def __init__(self, core=None):
        self.core = core
        self._commands = {'stop': self.stop,
                          'response': self.response}

        self._responses = {}
        self._resp_lock = Condition()

        self.halt = False

    @classmethod
    def build(cls, core):
        return {'status': -1, 'msg': 'Not implemented'}

    def clean(self):
        pass

    # Start all the stuff the unit needs
    def start(self):
        pass
        #print('[{0}.start] Starting ...'.format(self.name))


    def add_cmd_handler(self, command, handler):
        self._commands[command] = handler

    def get_response(self, channel, block=False):

        self._resp_lock.acquire()

        if (channel not in self._responses) and (not block):
            self._resp_lock.release()
            return {'status':-1}

        #print('[{0}] waiting for response'.format(self.name))
        while channel not in self._responses:
            self._resp_lock.wait()
        #print('[{0}] response received'.format(self.name))

        response = self._responses[channel]
        del(self._responses[channel])
        self._resp_lock.release()

        return response

    #################################################
    # These are default handlers for basic commands #
    #################################################
    def stop(self, message):
        self.halt = True

        return {'status': 0}

    def response(self, message):
        #print('[{0}.response] message: {1}'.format(self.name, tools.msg_to_str(message)))
        channel = message['channel']

        self._resp_lock.acquire()
        self._responses[channel] = message['params']
        self._resp_lock.notify_all()
        self._resp_lock.release()

        return {'status':0}

    ''' ############################################
    '''
    def forward(self, message):
        return self.core.dispatch(message)


    def digest(self, message):
        #print('[{0}.digest] {1}'.format(self.name, tools.msg_to_str(message)))
        command = message['cmd']
        if command in self._commands:
            result = self._commands[command](message)
            return result

        return {'status':-1, 'error':'command not found'}


    def dispatch(self, message):
        #print('[{0}.dispatch] {1}'.format(self.name, Message(message)))
        if message['dst'] == self.name:
            return self.digest(message)
        else:
            return self.forward(message)
