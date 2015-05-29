
import json
import cherrypy

from units.engine.orm import *


class UIApi:

    def __init__(self):
        self._db_mgr = ORM()
        print('[UUUUUUUUUU] {0}'.format(self._db_mgr.session_lock))

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

        errors = 0
        results_list = []
        self._db_mgr.session_lock.acquire()
        for rows in cherrypy.request.json:
            results = {}
            for table, row in rows.items():
                result = self._db_mgr.set(table, row)
                results[table] = result
                if result['status'] < 0:
                    errors += 1
            results_list.append(results)
        self._db_mgr.session_lock.release()

        print('[knowledge] saliendo de "set" - {1} - {0}'.format(results_list, errors))

        return {'status':errors, 'results':results_list}


    @cherrypy.expose
    @cherrypy.tools.json_out()
    def upload(self, content, params):
        print("UPLOAD")

        json_params = json.loads(params)

        print('[uiapi.upload] content: {0}'.format(content))
        print('[uiapi.upload] json_params: {0}'.format(json_params))

        print(content.file.read(8192))

        return {'status':0}
