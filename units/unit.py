
import random

class Unit:

	def __init__(self, core=None):
		self.core = core
		self.sync_commands  = {}
		self.async_commands = {}

	def start(self):
		pass

	def halt(self):
		pass

	def wait(self):
		pass

	def make_msg(self, dst, cmd, params={}, response=True):
		message = {'dst':dst,
		           'cmd':cmd,
		           'id' :self.gen_token(),
		           'params' : params.copy()}
		if response:
			message['src'] = self.name
		return message

	def make_response(self, message):
		response = message.copy()
		response['dst'] = message['src']
		response['src'] = message['dst']
		response['cmd'] = 'response'

		return response

	def gen_token(self):
		return random.getrandbits(32)

	''' This method control if the message have all the things
		that it should have.
	'''
	def check_msg(self, message):

		if not 'id' in message:
			message['id'] = self.gen_token()

		if not 'src' in message:
			message['src'] = self.name

		return True

	''' ############################################
	'''
	def forward(self, message):
		self.core.dispatch(message)

	def digest(self, message):
		print('[{0}] Digesting command {1}'.format(self.name, message['cmd']))
		command = message['cmd']
		if 'async' in message and not message['async']:
			if command in self.sync_commands:
				self.sync_commands[command](message)
		else:
			if command in self.async_commands:
				self.async_commands[command](message)

	def dispatch(self, message):
		if message['dst'] == self.name:
			self.digest(message)
		else:
			self.forward(message)
		
