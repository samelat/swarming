
import time
import json

from units.modules import tools
from units.brain.orm import *


class Knowledge:

    def __init__(self, brain):
        self._brain = brain
        self._db_mgr = DBMgr()

    def start(self):
        self._db_mgr.start()

    def timestamp(self):
        return int(time.time() * 1000)

    ''' ############################################
    '''
    def add_sunits(self, message):
        print('[knowledge] add_sunits Message - {0}'.format(message))

        #params = tools.restrict(message, SubUnit.params)
        sunit = message['params']['sunit']
        context = message['params']['context']
        sunit = SubUnit(**subunit)
        sunit.timestamp = self.timestamp()

        self._db_mgr.add(sunit)

        return {'sunit_id':sunit.sunit_id}

    def get_sunits(self, message):
        print('[knowledge] get_sunits Message - {0}'.format(message))
        params = message['params']

        timestamp = 0
        if 'timestamp' in params:
            timestamp = params['timestamp']

        sunits = []
        for sunit, inst in self._db_mgr.session.query(SubUnit).join(Instance).\
                                                filter(SubUnit.timestamp > timestamp).\
                                                all():
            sunit = {}
            sunit['']

            sunits.append(sunit)

        return {'timestamp':timestamp, 'sunits':sunits}
