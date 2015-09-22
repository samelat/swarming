
from units.engine.orm import *


# The idea of this class is implement a RESTful interface
# to access to database.
class Knowledge:

    def __init__(self, engine):
        self._engine = engine
        self._db_mgr = ORM()

    ############################################
    #
    ############################################
    def post(self, message):
        result = {'status': 0, 'results': []}

        self._db_mgr.session_lock.acquire()
        try:
            table = message['params']['entity']
            entries = message['params']['entries']
            entries = entries if isinstance(entries, list) else [entries]

            result['result'] = self._db_mgr.post(table, entries)

            self._db_mgr.session.commit()
            self._db_mgr.session_lock.release()

        except KeyError:
            result = {'status': -1}

        return result

    ############################################
    #
    ############################################
    def put(self, message):
        result = {'status': 0, 'results': []}

        self._db_mgr.session_lock.acquire()
        try:
            table = message['params']['entity']
            entries = message['params']['entries']
            entries = entries if isinstance(entries, list) else [entries]
            entries = [entry for entry in entries if 'id' in entry]

            result['result'] = self._db_mgr.put(table, entries)

            self._db_mgr.session.commit()
            self._db_mgr.session_lock.release()

        except KeyError:
            result = {'status': -1}

        return result

    ############################################
    #
    ############################################
    def get(self, message):
        result = {'status': 0, 'results': []}

        self._db_mgr.session_lock.acquire()
        try:
            table = message['params']['entity']
            conditions = message['params']['conditions']

            if isinstance(conditions, dict):
                result['result'] = self._db_mgr.get(table, conditions)
            else:
                result = {'status': -2, 'error': 'Bad "conditions" object.'}

            self._db_mgr.session.commit()
            self._db_mgr.session_lock.release()

        except KeyError:
            result = {'status': -1}

        return result

    ############################################
    #
    ############################################
    def delete(self, message):
        result = {'status': 0}

        self._db_mgr.session_lock.acquire()

        try:
            table = message['params']['entity']
            entries = message['params']['entries']
            entries = [entry for entry in entries if 'id' in entry]

            self._db_mgr.delete(table, entries)

        except KeyError:
            result = {'status': -1}

        self._db_mgr.session_lock.release()

        return result

