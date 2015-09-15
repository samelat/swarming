
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
        #print('[uiapi.get] JSON: {0}'.format(cherrypy.request.json))
        queries = cherrypy.request.json

        for query in queries:
            try:
                self.orm.entities[query['entity']]
            except KeyError:
                return {'status':-1, 'msg':'Entity does not exist', 'entity':query['entity']}

        self.orm.session_lock.acquire()

        results = []
        for query in queries:

            entity = self.orm.entities[query['entity']]
            orm_query = self.orm.session.query(entity)

            # Conditions that have to be applied
            if 'conditions' in query:
                for field, value in query['conditions'].items():
                    if field == 'timestamp':
                        orm_query = orm_query.filter(entity.timestamp > value)
                    else:
                        orm_query = orm_query.filter(getattr(entity, field) == value)

            # Query limit and offset
            if 'limit' in query:
                orm_query = orm_query.limit(query['limit'])
                if 'offset' in query:
                    orm_query = orm_query.offset(query['offset'])

            if ('aggregate' in query) and (query['aggregate'] == 'count'):
                count = orm_query.count()
                results.append({'count':count})

            else:
                rows = orm_query.all()
                json_rows = [row.to_json() for row in rows]

                results.append({'rows':json_rows})

        timestamp = self.orm.timestamp()
        
        self.orm.session_lock.release()

        return {'status':0, 'results':results, 'timestamp':timestamp}

    
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def set(self):
        #print('[uiapi.set] JSON: {0}'.format(cherrypy.request.json))

        results_list = []
        self.orm.session_lock.acquire()
        for rows in cherrypy.request.json:
            results = {}
            for table, row in rows.items():
                result = self.orm.set(table, row)
                results[table] = result
            results_list.append(results)
        self.orm.session.commit()
        self.orm.session_lock.release()

        #print('[knowledge] saliendo de "set" - {1} - {0}'.format(results_list, errors))

        return {'status':0, 'results':results_list}


    @cherrypy.expose
    @cherrypy.tools.json_out()
    def upload(self, file, json_params):
        #print("UPLOAD")

        params = json.loads(json_params)

        #print('[uiapi.upload] file: {0}'.format(file))
        #print('[uiapi.upload] params: {0}'.format(json_params))

        try:
            parser = self.file_parsers[params['format']](self.orm)
            result = parser.digest(file, params)

        except IndexError:
            #print('[upload] KeyError')
            return {'status':-1}

        return result
