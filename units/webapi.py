
import json
import select
import socket
from multiprocessing import Process, Queue

from units.unit import Unit
from units.modules.messenger import Messenger


class WebAPI(Unit):

    name = 'webapi'

    def __init__(self, core):
        super(WebAPI, self).__init__(core)
        self._process = None
        self._messenger = Messenger(self)

        self._port = 4000
        self._addr = '127.0.0.1'
        self._halt = False

    def _manager(self):

        sock_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_fd.bind((self._addr, self._port))

        sock_fd.listen(8)
        sock_fd.setblocking(0)

        while not self._halt:
            #print('[webapi] New loop cicle - ({0})'.format(self._halt))
            ready = select.select([sock_fd], [], [], 0.5)
            if ready[0]:
                new_fd, clt = sock_fd.accept()
            else:
                continue

            print('[webapi] Conection from {0}:{1}'.format(*clt))

            data = None
            new_fd.setblocking(0)
            ready = select.select([new_fd], [], [], 0.5)
            if ready[0]:
                data = new_fd.recv(4096)
            else:
                new_fd.close()
                continue

            data = data.strip()

            #try:
            message = json.loads(data.decode('utf-8'))
            #except:
            #new_fd.send(b'{"error":1, "desc":"JSON format error"}')

            '''
                Here we should control if the message have the
                correct format.
            '''
            print('[webapi] Unchecked message: {0}'.format(message))
            self.check_msg(message)
            print('[webapi] Checked message: {0}'.format(message))

            self.dispatch(message)

            response = '{{"error":0, "id":{0}}}'.format(message['id'])
            new_fd.send(response.encode('utf-8'))

            new_fd.close()

            print('[webapi] Data received: ' + str(message))

        print('[webapi] Service halted')

        sock_fd.close()

    def _launcher(self):
        self.sync_commands['halt'] = self._sync_halt
        self.async_commands['response'] = self._async_response
        
        self._messenger.start(True)
        self._manager()

    ''' ############################################
    '''
    def _sync_halt(self, message):
        print('[webapi] Halting service ...')
        self._halt = True

    def _async_response(self, message):
        print('[webapi] Response message: {0}'.format(message))

    ''' ############################################
    '''
    def dispatch(self, message):
        self._messenger.push(message)

    def wait(self):
        self._process.join()

    def start(self):
        self._process = Process(target=self._launcher)
        self._process.start()