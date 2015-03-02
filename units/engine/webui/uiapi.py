
import cherrypy
from urllib.parse import urlparse

from units.engine.orm import *


class UIApi:

    def __init__(self):
        self._db_mgr = ORM()

    ''' ############################################
    '''
    @cherrypy.expose
    def default(self, *args,**kwargs):
        raise cherrypy.HTTPRedirect("/static/index.html")


    @cherrypy.expose
    def halt(self):
        cherrypy.engine.exit()


    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def task(self):
        print('[uiapi.task] JSON: {0}'.format(cherrypy.request.json))
        data = cherrypy.request.json
        if 'action' not in data:
            return {'status':-1, 'msg':'You have to specify an action'} 

        #####################################################
        if data['action'] == 'get':
            self._db_mgr.session_lock.acquire()

            query = self._db_mgr.session.query(Task)

            if 'limit' in data:
                query = query.limit(data['limit'])
                if 'offset' in data:
                    query = query.offset(data['offset'])

            tasks = query.all()
            rows = [task.to_json() for task in tasks]

            size = self._db_mgr.session.query(Task).count()

            self._db_mgr.session_lock.release()

            return {'status':0, 'size':size, 'rows':rows}

        #####################################################
        elif data['action'] == 'add':
            print('SETTING VALUES: {0}'.format(data['values']))
            values = data['values']

            uri = urlparse(values['uri'])

            task = {}
            task['protocol'] = uri.scheme
            task['hostname'] = uri.hostname
            task['port'] = uri.port
            task['path'] = uri.path
            task['stage'] = values['stage']
            task['state'] = values['state']

            if 'attrs' in values:
                task['attrs'] = values['attrs']

            self._db_mgr.session_lock.acquire()
            result = self._db_mgr.set('task', task)
            self._db_mgr.session_lock.release()

            return result

        return {'status':-2, 'msg':'Unknown action'}


    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def dictionary(self):
        print('[uiapi.dictionary] JSON: {0}'.format(cherrypy.request.json))
        data = cherrypy.request.json
        if 'action' not in data:
            return {'status':-1, 'msg':'You have to specify an action'} 

        #####################################################
        if data['action'] == 'get':
            self._db_mgr.session_lock.acquire()

            query = self._db_mgr.session.query(Dictionary)

            if 'limit' in data:
                query = query.limit(data['limit'])
                if 'offset' in data:
                    query = query.offset(data['offset'])

            dictionaries = query.all()
            rows = [task.to_json() for dictionary in dictionaries]

            size = self._db_mgr.session.query(Dictionary).count()

            self._db_mgr.session_lock.release()

            return {'status':0, 'size':size, 'rows':rows}

        #####################################################
        elif data['action'] == 'add':
            print('SETTING VALUES: {0}'.format(data['values']))

            return {'status':0}

        return {'status':-2, 'msg':'Unknown action'}
