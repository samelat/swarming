
from units.modules import tools
from units.modules.unit import Unit


class HTTP(Unit):

	name = 'http'

	def __init__(self, core):
		super(HTTP, self).__init__(core)

	''' ############################################
		Command handlers
	'''
	def _bforce(self, message):
		print('[i] Sync Bforce Message - {0}'.format(message))
		response = tools.make_response(message)
		self.dispatch(response)

	def _spider(self, message):
		print('[i] Sync Spider Message - {0}'.format(message))
		response = tools.make_response(message)
		self.dispatch(response)

	# I HAVE TO improve this
	def start(self):
		self.add_cmd_handler('bforce', self._bforce)
		self.add_cmd_handler('spider', self._spider)
