
import os
import cherrypy
from cherrypy.process import servers
from threading import Thread

from units.modules.unit import Unit
from units.modules.message import Message
from units.modules.messenger import Messenger


class UIApi:

    name = 'uiapi'

    def __init__(self, engine):
        self._engine = engine
        self._thread = None


    ''' ############################################
    '''
    def _launcher(self):
        
        # cherrypy fix
        servers.wait_for_occupied_port = self.__fake_wait_for_occupied_port
        cherrypy.config.update('units/uiapi/server.conf')
        cherrypy.config.update({'engine.autoreload_on': False,
                                'environment': 'embedded'})

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
    def request(self):
        '''
        channel = tools.gen_token()
        message = cherrypy.request.json
        message['channel'] = channel
        message['src'] = self._webui.name

        self._webui.register_resp(channel)
        self._webui.dispatch(message)

        self._lost_responses[channel] = 0
        '''

        #return {'status':0, 'channel':channel}
        return {'status':0}

    
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def response(self):
        #data = cherrypy.request.json
        #print('[webui.response] {0}'.format(data))
        '''
        _responses = self._webui.get_responses(data['channels'])

        responses = {}
        for channel in _responses:
            try:
                responses[channel] = _responses[channel]['params']
                del(self._lost_responses[channel])
            except KeyError:
                print('[webui.error] Response Channel {0} does not exits'.format(channel))

        # With this we ensure that the ignored responses will be deleted
        to_remove = []
        for channel, count in self._lost_responses.items():
            self._lost_responses[channel] += 1
            if count > 3:
                to_remove.append(channel)
        self._webui.get_responses(to_remove)
        for channel in to_remove:
            del(self._lost_responses[channel])
        print('[webui.deleting] Deleting old responses: {0}'.format(to_remove))
        '''

        return {'status':0}
        #return {'status':0, 'responses':responses, 'channels':list(_responses.keys())}
