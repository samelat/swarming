
import json
import select
import socket
from multiprocessing import Process, Queue

from units.unit import Unit
from units.modules.messenger import Messenger


class JSONIface(Unit):

    name = 'jsoniface'

    def __init__(self, core):
        super(JSONIface, self).__init__(core)
        self._process = None
        self._messenger = None

        self._port = 4000
        self._addr = '127.0.0.1'
        self._halt = False

    def _manager(self):

        sock_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_fd.bind((self._addr, self._port))

        sock_fd.listen(8)
        sock_fd.setblocking(0)

        while not self._halt:
            print('[!] New loop cicle - ({0})'.format(self._halt))
            ready = select.select([sock_fd], [], [], 2)
            if ready[0]:
                new_fd, clt = sock_fd.accept()
            else:
                continue

            print('[!] Conection from {0}:{1}'.format(*clt))

            data = None
            new_fd.setblocking(0)
            ready = select.select([new_fd], [], [], 2)
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
            print('[!] Unchecked message: {0}'.format(message))
            self.check_msg(message)
            print('[!] Checked message: {0}'.format(message))

            self.dispatch(message)

            response = '{{"error":0, "id":{0}}}'.format(message['id'])
            new_fd.send(response.encode('utf-8'))

            new_fd.close()

            print('[!] Data received: ' + str(message))

        print('[i] WebAPI halted')

        sock_fd.close()

    ''' ############################################
    '''
    def dispatch(self, message):
        self._messenger.push(message)

    def halt(self):
        print('[!] Halting JSONIface ...')
        self._halt = True
        self._process.join()
        print('[!] JSONIface halted')

    def test(self):
        self._messenger = Messenger(self)
        self._messenger.start(True)
        self._manager()

    def start(self):
        self._process = Process(target=self.test)
        self._process.start()