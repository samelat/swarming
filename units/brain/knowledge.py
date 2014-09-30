
import time
import json

from units.modules import tools
from units.brain.orm import *


class Knowledge:

    def __init__(self, brain):
        self._brain = brain
        self._db_mgr = DBMgr()
        self._table_classes = self._db_mgr.get_table_classes()

    def start(self):
        self._db_mgr.start()

    def timestamp(self):
        return int(time.time() * 1000)

    ''' ############################################
    '''
    def set(self, message):
        params = message['params']
        print('[knowledge] "add" message - {0}'.format(params))

        table_class = self._table_classes[params['table']]

        row = table_class.from_json(params['values'], self._db_mgr)
        #row.timestamp = self.timestamp()
        #self._db_mgr.add(row)

        return {'id':row.id}


    def get(self, message):
        params = message['params']
        print('[knowledge] "get" message - {0}'.format(params))

        timestamp = 0
        if 'timestamp' in params:
            timestamp = params['timestamp']

        table_class = self._table_classes[params['table_name']]
        json_rows = []
        for row in self._db_mgr.session.query(table_class).\
                                           filter(table_class.timestamp > timestamp).\
                                           all():
            json_row = row.to_json()
            json_rows.append(json_row)

        if json_rows:
            timestamp = self.timestamp()

        return {'timestamp':timestamp, 'rows':json_rows}

