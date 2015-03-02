
import os
import cherrypy
from cherrypy.process import servers
from threading import Thread
from urllib.parse import urlparse

from units.modules.unit import Unit
from units.modules.message import Message
from units.modules.messenger import Messenger

from units.engine.orm import *


class UIApi:

    name = 'uiapi'

    def __init__(self, engine):
        self._engine = engine
        self._db_mgr = None
        self._thread = None


    ''' ############################################
    '''
    def _launcher(self):

        self._db_mgr = ORM()
        print('[AAAAAAAAAA] {0}'.format(self._db_mgr.session_lock))
        
        # cherrypy fix
        servers.wait_for_occupied_port = self.__fake_wait_for_occupied_port
        cherrypy.config.update('units/uiapi/server.conf')
        cherrypy.config.update({'engine.autoreload_on': False})

        conf = {
            '/static':{
                'tools.staticdir.root': os.path.abspath(os.getcwd()),
                'tools.staticdir.on': True,
                'tools.staticdir.dir': 'units/uiapi/html'
            }
        }
        
        cherrypy.quickstart(self, '/', conf)


    def __fake_wait_for_occupied_port(self, host, port):
        return


    def start(self):
        print('[webui] Starting')
        self._thread = Thread(target=self._launcher)
        self._thread.start()


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
