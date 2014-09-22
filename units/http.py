
import time

from units.modules import tools
from units.modules.unit import Unit


class HTTP(Unit):

	is_border_unit = True
	name = 'http'

	protocols = ['http', 'https']

	def __init__(self, core):
		super(HTTP, self).__init__(core)

	def start(self):
		print('[http] Staring')
		self.add_cmd_handler('digest', self.digest)

	''' ############################################
		Command handlers
	'''
	def digest(self, message):
		print('[i] Sync Digest Message - {0}'.format(message))
		for c in range(1, 7):
			print('[http] Waiting cicle {0}'.format(c))
			time.sleep(10)
		return {'status':'done'}

