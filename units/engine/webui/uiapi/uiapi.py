
import json
import cherrypy

from units.engine.orm import *
from units.engine.webui.uiapi.csv import CSV

class UIApi:

    def __init__(self):
        self.orm = ORM()
        self.file_parsers = {'csv':CSV}


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
            entity = self.orm.entities[data['entity']]
        except KeyError:
            return {'status':-1, 'msg':'Malformed data [{0}]'.format(data)}

        self.orm.session_lock.acquire()

        query = self.orm.session.query(entity)

        # Conditions that have to be applied
        if 'conditions' in data:
            for condition, value in data['conditions'].items():
                if condition == 'timestamp':
                    query = query.filter(entity.timestamp > value)

        # Query limit and offset
        if 'limit' in data:
            query = query.limit(data['limit'])
            if 'offset' in data:
                query = query.offset(data['offset'])

        timestamp = self.orm.timestamp()
        if ('aggregate' in data) and (data['aggregate'] == 'count'):
            count = query.count()
            result = {'status':0, 'count':count, 'timestamp':timestamp}

        else:
            rows = query.all()
            json_rows = [row.to_json() for row in rows]

            size = self.orm.session.query(entity).count()

            result = {'status':0, 'size':size, 'rows':json_rows}

        self.orm.session_lock.release()

        return result

    
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def set(self):
        print('[uiapi.set] JSON: {0}'.format(cherrypy.request.json))

        results_list = []
        self.orm.session_lock.acquire()
        for rows in cherrypy.request.json:
            results = {}
            for table, row in rows.items():
                result = self.orm.set(table, row)
                results[table] = result
            results_list.append(results)
        self.orm.session_lock.release()

        print('[knowledge] saliendo de "set" - {1} - {0}'.format(results_list, errors))

        return {'status':0, 'results':results_list}


    @cherrypy.expose
    @cherrypy.tools.json_out()
    def upload(self, file, json_params):
        print("UPLOAD")

        params = json.loads(json_params)

        print('[uiapi.upload] file: {0}'.format(file))
        print('[uiapi.upload] params: {0}'.format(json_params))

        try:
            parser = self.file_parsers[params['format']](self.orm)
            result = parser.digest(file, params)

        except IndexError:
            print('[upload] KeyError')
            return {'status':-1}

        return result
