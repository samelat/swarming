
import os
import cherrypy
from cherrypy.process import servers
from threading import Thread

from units.engine.webui.uiapi import UIApi


class WebUI:

    name = 'webui'

    def __init__(self, engine):
        self._engine = engine
        self._thread = None


    ''' ############################################
    '''
    def _launcher(self):
        
        # cherrypy fix
        servers.wait_for_occupied_port = self.__fake_wait_for_occupied_port
        cherrypy.config.update('units/engine/webui/server.conf')
        cherrypy.config.update({'engine.autoreload_on': False})

        conf = {
            '/static':{
                'tools.staticdir.root': os.path.abspath(os.getcwd()),
                'tools.staticdir.on': True,
                'tools.staticdir.dir': 'units/engine/webui/html'
            }
        }
        
        cherrypy.quickstart(UIApi(), '/', conf)


    def __fake_wait_for_occupied_port(self, host, port):
        return


    def start(self):
        print('[webui] Starting')
        self._thread = Thread(target=self._launcher)
        self._thread.start()
