
from units.modules import tools


class Unit:

    def __init__(self, core=None):
        self.core = core
        self._commands  = {'halt':self.halt,
                           'response':self.response}

        self.responses = {}

    # Start all the things the unit needs
    def start(self):
        pass

    # Wait until the until finish
    def wait(self):
        pass

    def add_cmd_handler(self, command, handler):
        self._commands[command] = handler

    ''' ############################################
        These are default handlers for the basic commands
    '''
    def halt(self, message):
        pass

    def response(self, message):
        channel_id = message['id']
        if channel_id in self.responses:
            self.responses[channel_id] = message

    ''' ############################################
    '''
    def forward(self, message):
        self.core.dispatch(message)

    def digest(self, message):
        print('[{0}] Digesting command {1}'.format(self.name, message['cmd']))
        command = message['cmd']
        if command in self._commands:
            self._commands[command](message)

    def dispatch(self, message):
        if message['dst'] == self.name:
            self.digest(message)
        else:
            self.forward(message)
        
