
from units.modules import tools
from units.tasker.orm import *


class Knowledge:

    def __init__(self, tasker):
        self._tasker = tasker
        self._db_mgr = ORM()

    ''' ############################################
        This set and get methods are just to keep an abstract
        implementation of the database manager. This allow us
        to change to mongodb (for example) in the future if we
        want to.
    '''
    def set(self, message):
        params = message['params']
        print('[knowledge] "set" message - {0}'.format(params))

        self._db_mgr.session_lock.acquire()
        row_id = self._db_mgr.set(params['table'], params['values'])
        self._db_mgr.session_lock.release()

        return {'id':row_id}


    def get(self, message):
        params = message['params']
        print('[knowledge] "get" message - {0}'.format(params))

        timestamp = 0
        if 'timestamp' in params:
            timestamp = params['timestamp']

        self._db_mgr.session_lock.acquire()
        result = self._db_mgr.get(params['table'], timestamp)
        self._db_mgr.session_lock.release()

        return result

