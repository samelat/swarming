
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
        sunit = SubUnit(**subunit)
        self._db_mgr.add(sunit)

        response = tools.make_response(message)
        response['params']['subunit']['sunit_id'] = sunit.sunit_id

        self._brain.dispatch(response)
        print('[knowledge] responding - {0}'.format(response))

    def start(self):
        self._db_mgr.start()
