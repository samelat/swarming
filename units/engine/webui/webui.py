
import os
import cherrypy
from cherrypy.process import servers
from threading import Thread

from units.engine.webui.api import FilesAPI
from units.engine.webui.api import TasksAPI
from units.engine.webui.api import UnitsAPI
from units.engine.webui.api import DictionariesAPI


class WebUI:

    name = 'webui'

    def __init__(self, engine):
        self._engine = engine
        self._thread = None

    #############################################
    #############################################
    def _launcher(self):
        
        # CherryPy fix
        servers.wait_for_occupied_port = self.__fake_wait_for_occupied_port
        
        cherrypy.config.update('units/engine/webui/server.conf')

        global_conf = {
            'engine.autoreload_on': False,
            'log.error_file': 'log/webui.global.error.log',
            'log.access_file': 'log/webui.global.access.log'
        }

        cherrypy.log.error_log.propagate = True
        cherrypy.log.access_log.propagate = False

        cherrypy.config.update(global_conf)

        static_conf = {
            '/ui': {
                'tools.staticdir.root': os.path.abspath(os.getcwd()),
                'tools.staticdir.on': True,
                'tools.staticdir.dir': 'units/engine/webui/html'
            }
        }

        api_conf = {
            '/': {
                # 'log.error_file': 'log/webui.api.error.log',
                # 'log.access_file': 'log/webui.api.access.log',
                'request.dispatch': cherrypy.dispatch.MethodDispatcher()
            }
        }
        
        cherrypy.tree.mount(self, '/', config=static_conf)
        cherrypy.tree.mount(FilesAPI(), '/api/files', config=api_conf)
        cherrypy.tree.mount(TasksAPI(), '/api/tasks', config=api_conf)
        cherrypy.tree.mount(UnitsAPI(), '/api/units', config=api_conf)
        cherrypy.tree.mount(DictionariesAPI(), '/api/dictionaries', config=api_conf)
        # cherrypy.tree.mount()

        cherrypy.engine.start()
        cherrypy.engine.block()

    #############################################
    #############################################
    @cherrypy.expose
    def default(self, *args, **kwargs):
        raise cherrypy.HTTPRedirect("/ui/index.html")

    def __fake_wait_for_occupied_port(self, host, port):
        return

    def start(self):
        self._thread = Thread(target=self._launcher)
        self._thread.start()

    def stop(self):
        cherrypy.engine.exit()
        self._thread.join()
