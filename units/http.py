
from units.unit import Unit

class HTTP(Unit):

	name = 'http'

	def __init__(self, core):
		super(HTTP, self).__init__(core)

	''' Async Messages
	'''
	def _async_bforce(self, message):
		print('[i] Async Bforce Message - {0}'.format(message))

	def _async_spider(self, message):
		print('[i] Async Spider Message - {0}'.format(message))

	''' Sync Messages
	'''
	def _sync_bforce(self, message):
		print('[i] Sync Bforce Message - {0}'.format(message))

	def _sync_spider(self, message):
		print('[i] Sync Spider Message - {0}'.format(message))

	# I HAVE TO improve this
	def start(self):
		self.sync_commands['bforce'] = self._sync_bforce
		self.async_commands['bforce'] = self._async_bforce

		self.sync_commands['spider'] = self._sync_spider
		self.async_commands['spider'] = self._async_spider