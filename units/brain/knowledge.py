
import traceback

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
    def set(self, message):
        params = message['params']
        print('[knowledge] "add" message - {0}'.format(params))

        table_class = self._db_mgr.tables[params['table']]

        try:
            row = table_class.from_json(params['values'], self._db_mgr.session)
            row_id = row.id
        except:
            traceback.print_exc()
            row_id = -1
        #row.timestamp = self.timestamp()
        #self._db_mgr.add(row)
        self._db_mgr.session.commit()

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

