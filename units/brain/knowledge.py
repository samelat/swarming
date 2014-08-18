
import json

from units.modules import tools
from units.brain.orm import *


class Knowledge:

    def __init__(self, brain):
        self._brain = brain
        self._db_mgr = DBMgr()

    def add_subunit(self, message):
        print('[knowledge] add_subunit Message - {0}'.format(message))

        #params = tools.restrict(message, SubUnit.params)
        subunit = message['params']['subunit']
        context = message['params']['context']
        self._db_mgr.add(SubUnit(**subunit))

        # response = tools.make_response(message)
        # self.dispatch(response)
        # print('[brain] Sync add_target Message - {0}'.format(message))

    def start(self):
        self._db_mgr.start()
