
import cherrypy

from units.engine.orm import ORM


class JsonAPI:

    exposed = True

    def __init__(self, entity):
        self.orm = ORM()
        self.entity = entity

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def PUT(self, eid=0):
        print('[!] PUT: {0}'.format(cherrypy.request.json))

        entity = self.orm.entities[self.entity]

        return {'status': 0}

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def POST(self):
        try:
            entries = cherrypy.request.json if isinstance(cherrypy.request.json, list) else [cherrypy.request.json]

            self.orm.session_lock.acquire()

            result = self.orm.post(self.entity, entries)

        except KeyError:
            result = {'status': -1}

        self.orm.session_lock.release()

        return result

    @cherrypy.tools.json_out()
    def GET(self, eid=0, limit=20, offset=0, count=False):

        entity = self.orm.entities[self.entity]
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
    def DELETE(self, eid):

        entity = self.orm.entities[self.entity]

        self.orm.session_lock.acquire()

        self.orm.session.query(entity).filter(entity.id == int(eid)).delete()
        if deleted:
            self.orm.session.commit()

        self.orm.session_lock.release()

        return {'status': 0}



