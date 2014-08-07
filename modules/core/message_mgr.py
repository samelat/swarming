
from threading import Thread
from threading import Condition

class MessageMgr:

    def __init__(self, core):
        self._core = core
        self._msg_cond = Condition()
        self._messages = []
        self._thread = None

        self.halt = False

    def _manager(self):
    	print('[mm] Started')
    	while not self.halt:
    		message = self.pop()
    		print('[mm] message: {0}'.format(message))

    def push(self, message):
    	self._msg_cond.acquire()
    	self._messages.insert(0, message)
    	self._msg_cond.notify()
    	self._msg_cond.release()

    def pop(self):
    	self._msg_cond.acquire()
    	self._msg_cond.wait_for(lambda: len(self._messages) > 0)
    	message = self._messages.pop()
    	self._msg_cond.release()
    	return message

    def start(self):
    	self._thread = Thread(target=self._manager)
    	self._thread.start()