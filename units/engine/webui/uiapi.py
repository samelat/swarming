
import cherrypy

from units.engine.orm import *


class UIApi:

    def __init__(self):
        self._db_mgr = ORM()

    @cherrypy.expose
    def halt(self):
        cherrypy.engine.exit()


    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def get(self):
        print('[uiapi.get] JSON: {0}'.format(cherrypy.request.json))
        data = cherrypy.request.json

        try:
            entity = self._db_mgr.entities[data['entity']]
        except KeyError:
            return {'status':-1, 'msg':'Malformed data [{0}]'.format(data)}

        self._db_mgr.session_lock.acquire()

        query = self._db_mgr.session.query(entity)

        if 'limit' in data:
            query = query.limit(data['limit'])
            if 'offset' in data:
                query = query.offset(data['offset'])

        rows = query.all()
        json_rows = [row.to_json() for row in rows]

        size = self._db_mgr.session.query(entity).count()

        self._db_mgr.session_lock.release()

        return {'status':0, 'size':size, 'rows':json_rows}

    
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def set(self):
        print('[uiapi.set] JSON: {0}'.format(cherrypy.request.json))

        data = cherrypy.request.json

        try:
            entity = data['entity']
            values = data['values']
        except KeyError:
            return {'status':-1, 'msg':'Malformed data [{0}]'.format(data)}

        self._db_mgr.session_lock.acquire()
        result = self._db_mgr.set(entity, values)
        self._db_mgr.session_lock.release()

        return result
