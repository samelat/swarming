
from threading import Lock

from units.modules import tools


class Unit:

    tid = '0'

    def __init__(self, core=None):
        self.core = core
        self._commands  = {'halt':self.halt,
                           'response':self.response}

        self._responses = {}
        self._resp_lock = Lock()
        self._resp_handlers = {}

        self.halt = False

    def unit_id(self):
        return '{0}:{1}'.format(self.uname, self.tid)

    # Start all the things the unit needs
    def start(self):
        pass

    # Wait until the unit finish
    def wait(self):
        pass

    def add_cmd_handler(self, command, handler):
        self._commands[command] = handler

    def add_resp_handler(self, channel, handler):
        self._resp_handlers[channel] = handler

    def get_responses(self, channels):
        responses = {}

        self._resp_lock.acquire()

        for channel in channels:
            if (channel in self._responses) and (self._responses[channel] != None):
                responses[channel] = self._responses[channel]
                self._responses[channel] = None
        self._resp_lock.release()
        return responses

    def register_resp(self, channel):
        self._resp_lock.acquire()
        self._responses[channel] = None
        self._resp_lock.release()


    ''' ############################################
        These are default handlers for the basic commands
    '''
    def halt(self, message):
        self.halt = True

    def response(self, message):
        print('[{0}] Response: {1}'.format(self.unit_id(), message))
        channel = message['channel']

        if channel in self._resp_handlers:
            self._resp_handlers(message)
        else:
            self._resp_lock.acquire()
            if channel in self._responses:
                self._responses[channel] = message
            self._resp_lock.release()

    ''' ############################################
    '''
    def forward(self, message):
        self.core.dispatch(message)

    def digest(self, message):
        print('[{0}] Digesting command {1}'.format(self.unit_id(), message['cmd']))
        command = message['cmd']
        if command in self._commands:
            params = self._commands[command](message)
            response = tools.make_response(message)
            if response:
                response['params'].update(params)
                print('[{0}] responding - {1}'.format(self.unit_id(), response))
                self.dispatch(response)

    def dispatch(self, message):
        if message['dst'] == self.unit_id():
            self.digest(message)
        else:
            self.forward(message)
        
