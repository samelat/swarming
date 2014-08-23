
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
    def add_sunit(self, message):
        print('[knowledge] add_sunit Message - {0}'.format(message))

        #params = tools.restrict(message, SubUnit.params)
        _sunit = message['params']['sunit']
        _context = message['params']['context']

        sunit = SubUnit(**_sunit)
        sunit.timestamp = self.timestamp()
        sunit.state = 'stopped'
        self._db_mgr.add(sunit)

        return {'sunit_id':sunit.sunit_id}

    def get_sunits(self, message):
        print('[knowledge] get_sunits Message - {0}'.format(message))
        params = message['params']

        timestamp = 0
        if 'timestamp' in params:
            timestamp = params['timestamp']

        sunits = []
        for sunit in self._db_mgr.session.query(SubUnit).\
                                          filter(SubUnit.timestamp > timestamp).\
                                          all():
            json_sunit = self._db_mgr.jsonify(sunit)
            sunits.append(json_sunit)

        if sunits:
            timestamp = self.timestamp()

        return {'timestamp':timestamp, 'sunits':sunits}
