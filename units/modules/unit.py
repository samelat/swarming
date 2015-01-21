
from threading import Lock

from units.modules import tools


class Unit:

    protocols = []

    def __init__(self, core=None):
        self.core = core
        self._commands  = {'halt':self.halt,
                           'response':self.response}

        self._responses = {}
        self._resp_lock = Lock()
        self._resp_handlers = {}

        self.halt = False

    # Start all the things the unit needs
    def start(self):
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

    ''' The aim of these methods is to simplify the tasker's knowledge accesses
    '''
    def set_knowledge(self, values):
        message = {'src':self.name, 'dst':'tasker', 'cmd':'set',
                   'params':{'table':'unit',
                             'values':values}}
        return self.core.dispatch(message)

    def get_knowledge(self, values, async=True):
        message = {'src':self.name, 'dst':'tasker', 'cmd':'get',
                   'params':{'table':'unit',
                             'values':values}}
        result = self.core.dispatch(message)
        if async:
            return result

        while True:
            response = self.get_responses(result['channel'])
            if response:
                return response

    def register(self):
        values = {'name':self.name,
                  'protocols':[{'name':protocol} for protocol in self.protocols]}
        self.set_knowledge(values)
        print('[unit.register] {0}'.format(result))

    ''' ############################################
        These are default handlers for the basic commands
    '''
    def halt(self, message):
        self.halt = True

    def response(self, message):
        print('[{0}.response] message: {1}'.format(self.name, tools.msg_to_str(message)))
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
        print('[{0}.digest] message: {1}'.format(self.name, tools.msg_to_str(message)))
        command = message['cmd']
        if command in self._commands:
            result = self._commands[command](message)
            response = tools.make_response(message)
            if response:
                response['params'].update(result)
                print('[{0}.digest] response - {1}'.format(self.name, result))
                self.dispatch(response)

    def dispatch(self, message):
        if message['dst'] == self.name:
            self.digest(message)
        else:
            self.forward(message)
        
