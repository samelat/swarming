
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

	def make_msg(self, dst, cmd, params={}, response=True):
		message = {'dst':dst,
		           'cmd':cmd,
		           'id' :self.gen_token(),
		           'params' : params.copy()}
		if response:
			message['src'] = self.name
		return message

	def gen_token(self):
		return random.getrandbits(32)

	''' This method control if the message have all the things
		that it should have.
	'''
	def check_msg(self, message):

		if not message.has_key('id'):
			message['id'] = self.gen_token()

		if not message.has_key('src'):
			message['src'] = self.name

		return True

	''' TODO: Maybe I could improve this method
	'''
	def dispatch(self, message):
		command = message['command']

		if message.has_key('async') and not message['async']:
			if command in self.sync_commands:
				self.sync_commands[command](message)
		else:
			if command in self.async_commands:
				self.async_commands[command](message)
