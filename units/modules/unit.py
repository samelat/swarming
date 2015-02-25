
from threading import Condition

from units.modules.message import Message


class Unit:

    light = False
    protocols = []

    def __init__(self, core=None):
        self.core = core
        self._commands  = {'halt':self.halt,
                           'response':self.response}

        self._responses = {}
        self._resp_lock = Condition()

        self.halt = False


    @classmethod
    def build(cls, core):
        return {'status':-1, 'msg':'Not implemented'}


    def clean(self):
        pass
    

    # Start all the things the unit needs
    def start(self):
        print('[{0}.start] Starting ...'.format(self.name))


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


    ''' The aim of these methods is to simplify the tasker knowledge accesses
    '''
    def set_knowledge(self, row=None, block=True, rows=[]):
        #print('[{0}] set_knowledge: {1}'.format(self.name, values))

        _rows = []

        if row:
            _rows.insert(0, row)

        if rows:
            _rows.extend(rows)

        if not _rows:
            return {'status':-3}

        message = {'src':self.name, 'dst':'engine', 'cmd':'set', 'params':_rows}
        result = self.core.dispatch(message)
        
        if not block:
            return result

        # print('[{0}] set_knowledge dispatch result: {1}'.format(self.name, result))
        responses = self.get_response(result['channel'], True)

        # print('[{0}] set_knowledge response: {1}'.format(self.name, response))
        
        return responses

        #return {'status':0}


    def get_knowledge(self, values, block=True):
        message = {'src':self.name, 'dst':'engine', 'cmd':'get',
                   'params':{'unit':values}}
        result = self.core.dispatch(message)
        '''
        if not block:
            return result

        response = self.get_response(result['channel'], True)

        print('[get_knowledge] {0}'.format(response))
        
        return response'''

        return {'status':0}


    ''' ############################################
        These are default handlers for basic commands
    '''
    def halt(self, message):
        self.halt = True

        return {'status':0}


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
        '''
        if response:
            response['params'].update(result)
            print('[{0}.digest] response - {1}'.format(self.name, result))
            self.dispatch(response)
        '''


    def dispatch(self, message):
        # print('[{0}.dispatch] {1}'.format(self.name, Message(message)))
        if message['dst'] == self.name:
            return self.digest(message)
        else:
            return self.forward(message)
        
