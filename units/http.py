
import time

from units.modules import tools
from units.modules.unit import Unit


class HTTP(Unit):

	name = 'http'

	def __init__(self, core):
		super(HTTP, self).__init__(core)

	def start(self):
		print('[http] Staring')
		self.add_cmd_handler('bforce', self.bforce)
		self.add_cmd_handler('spider', self.spider)

	''' ############################################
		Command handlers
	'''
	def bforce(self, message):
		print('[i] Sync Bforce Message - {0}'.format(message))
		for c in range(1, 7):
			print('[http] Waiting cicle {0}'.format(c))
			time.sleep(10)
		return {'status':'done'}

	def spider(self, message):
		print('[i] Sync Spider Message - {0}'.format(message))
		return {'status':'done'}
