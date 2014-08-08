
from modules.unit import Unit
from modules.json_iface import JSONIface

from modules.core.task_mgr import TaskMgr
from modules.core.event_mgr import EventMgr
from modules.core.message_mgr import MessageMgr
from modules.core.dictionary_mgr import DictionaryMgr


class Core(Unit):

    def __init__(self):
        self._task_mgr    = TaskMgr(self)
        self._message_mgr = MessageMgr(self)

        self._json_iface  = JSONIface(self)

    def dispatch(self, message):
        self._message_mgr.push(message)

    '''

    '''
    def start(self):
        # First we start core components
        self._message_mgr.start()

        self._json_iface.start()

        print('[c] Waiting for the service...')
        self._json_iface.process.join()

        self._message_mgr.stop()
        self._message_mgr._thread.join()
