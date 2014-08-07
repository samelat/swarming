
import json
import socket
from multiprocessing import Process

class JSONIface:

	def __init__(self, core):
		self._core = core
		self._port = 4000
		self._addr = '127.0.0.1'

		self.process = None


	def _manager(self):

		sock_fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock_fd.bind((self._addr, self._port))

		sock_fd.listen(8)

		data = None
		while data != b'{}':

			new_fd, clt = sock_fd.accept()
			print('[!] Conection from {0}:{1}'.format(*clt))

			data = new_fd.recv(4096).strip()

			#try:
			json_data = json.loads(data)
			#except:
			#new_fd.send(b'{"error":1, "desc":"JSON format error"}')

			# Here we should control if the message have the correct format
			self._core.dispatch(data)

			new_fd.close()

			print('[!] Data received: ' + str(data))

		sock_fd.close()


	def start(self):
		self.process = Process(target=self._manager)
		self.process.start()