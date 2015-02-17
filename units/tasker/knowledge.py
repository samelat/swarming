
from units.tasker.orm import *


class Knowledge:

    def __init__(self, tasker, db_mgr):
        self._tasker = tasker
        self._db_mgr = db_mgr

    ''' ############################################
        These set and get methods are just to keep an abstract
        implementation of the database manager. This allow us
        to change to mongodb (for example) in the future if we
        want to.
    '''
    def set(self, message):
        params = message['params']
        #print('[knowledge] "set" message - {0}'.format(params))

        values = {}
        self._db_mgr.session_lock.acquire()
        for table, _values in params.items():
            result = self._db_mgr.set(table, _values)
            values[table] = result
        self._db_mgr.session_lock.release()

        return {'status':0, 'values':values}


    def get(self, message):
        params = message['params']
        #print('[knowledge] "get" message - {0}'.format(params))

        values = {}
        self._db_mgr.session_lock.acquire()
        for table, _values in params.items():
            rows = self._db_mgr.get(table, _values)
            values[table] = {table:rows}
        self._db_mgr.session_lock.release()

        return {'status':0, 'values':values}

