
import traceback

import time
import json

from units.modules import tools
from units.brain.orm import *


class Knowledge:

    def __init__(self, brain):
        self._brain = brain
        self._db_mgr = ORM()

    def start(self):
        self._db_mgr.start()

    def timestamp(self):
        return int(time.time() * 1000)

    ''' ############################################
        This set and get methods are just to keep an abstract
        implementation of the database manager. This allow us
        to change to mongodb (for example) in the future if we
        want to.
    '''
    def set(self, message):
        params = message['params']
        print('[knowledge] "set" message - {0}'.format(params))

        row_id = self._db_mgr.set(params['table'], params['values'])

        return {'id':row_id}


    def get(self, message):
        params = message['params']
        print('[knowledge] "get" message - {0}'.format(params))

        timestamp = 0
        if 'timestamp' in params:
            timestamp = params['timestamp']

        table_class = self._table_classes[params['table']]
        json_rows = []
        for row in self._db_mgr.session.query(table_class).\
                                           filter(table_class.timestamp > timestamp).\
                                           all():
            json_row = row.to_json()
            json_rows.append(json_row)

        if json_rows:
            timestamp = self.timestamp()

        return {'timestamp':timestamp, 'rows':json_rows}

