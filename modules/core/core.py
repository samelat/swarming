
from multiprocessing import Thread

from task_mgr import TaskMgr
from event_mgr import EventMgr
from message_mgr import MessageMgr
from dictionary_mgr import DictionaryMgr


class Core:

    def __init__(self):
        self._task_mgr    = TaskMgr(self)
        self._message_mgr = MessageMgr(self)

    '''

    '''
    def _start_task_mgr(self):
        pass

    '''

    '''
    def _start_message_mgr(self):
        pass

    '''

    '''
    def start_core(self):
        pass
