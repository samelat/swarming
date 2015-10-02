
import cherrypy

from units.engine.orm import *
# from units.engine.webui.uiapi.csv import CSV


class JsonAPI:

    exposed = True

    def __init__(self):
        self.orm = ORM()

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def PUT(self, entity_name, eid=0):
        # cherrypy.engine.exit()
        print('[!] PUT: {0}'.format(cherrypy.request.json))

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def POST(self, entity_name):
        try:
            entries = cherrypy.request.json if isinstance(cherrypy.request.json, list) else [cherrypy.request.json]

            self.orm.session_lock.acquire()

            result = self.orm.post(entity_name, entries)

        except KeyError:
            result = {'status': -1}

        self.orm.session_lock.release()

        return result

    @cherrypy.tools.json_out()
    def GET(self, entity_name, eid=0, limit=20, offset=0, count=False):
        try:
            entity = self.orm.entities[entity_name]
        except KeyError:
            return {'status': -1, 'error': 'Unknown entity "{0}"'.format(entity_name)}

        response = {'status': 0, 'result': [], 'timestamp': 0}

        self.orm.session_lock.acquire()

        orm_query = self.orm.session.query(entity)

        if eid:
            orm_query = orm_query.filter(entity.id == int(eid))

        else:
            # Conditions that have to be applied
            '''
            for field, value in query['conditions'].items():
                if field == 'timestamp':
                    orm_query = orm_query.filter(entity.timestamp > value)
                else:
                    orm_query = orm_query.filter(getattr(entity, field) == value)
            '''

            # Query limit and offset
            orm_query = orm_query.limit(limit).offset(offset)

        if count:
            count = orm_query.count()
            response['result'] = {'count': count}

        else:
            rows = orm_query.all()
            response['result'] = [row.to_json() for row in rows]

        response['timestamp'] = self.orm.timestamp()

        self.orm.session_lock.release()

        return response

    @cherrypy.tools.json_out()
    def DELETE(self, entity_name, eid=0):
        try:
            entity = self.orm.entities[entity_name]
        except KeyError:
            return {'status': -1, 'error': 'Unknown entity "{0}"'.format(entity_name)}

        self.orm.session_lock.acquire()

        deleted = self.orm.session.query(entity).filter(entity.id == int(entity_id)).delete()
        if deleted:
            self.orm.session.commit()

        self.orm.session_lock.release()

        return {'status': 0, 'deleted': deleted}



