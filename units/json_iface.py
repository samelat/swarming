
import json
import socket
from multiprocessing import Process

from units.unit import Unit


class JSONIface(Unit):

    name = 'jsoniface'

    def __init__(self, core):
        super(JSONIface, self).__init__(core)
        self._port = 4000
        self._addr = '127.0.0.1'
        self._halt = False
        self._process = None

    def _manager(self):

        sock_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_fd.bind((self._addr, self._port))

        sock_fd.listen(8)

        data = None
        while not self._halt:

            new_fd, clt = sock_fd.accept()
            print('[!] Conection from {0}:{1}'.format(*clt))

            data = new_fd.recv(4096).strip()

            #try:
            message = json.loads(data.decode('utf-8'))
            #except:
            #new_fd.send(b'{"error":1, "desc":"JSON format error"}')

            print('[!] Before message: {0}'.format(message))
            self.check_msg(message)
            print('[!] After message: {0}'.format(message))

            '''
                Here we should control if the message have the
                correct format
            '''
            self.core.dispatch(message)

            response = '{{"error":0, "id":{0}}}'.format(message['id'])
            new_fd.send(response.encode('utf-8'))

            new_fd.close()

            print('[!] Data received: ' + str(message))

        sock_fd.close()

    def halt(self):
        self._halt = True
        self._process.join()
        print('[!] JSONIface halted')

    def start(self):
        self._process = Process(target=self._manager)
        self._process.start()