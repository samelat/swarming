
from units.modules import tools
from units.modules.unit import Unit


class HTTP(Unit):

	_name = 'http'

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
		return {'status':'success'}

	def spider(self, message):
		print('[i] Sync Spider Message - {0}'.format(message))
		return {'status':'success'}
