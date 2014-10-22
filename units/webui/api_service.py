
import os
import cherrypy
from cherrypy.process import servers

from units.modules import tools


class APIService:

    def __init__(self, webui):
        self._webui = webui
        # cherrypy fix
        servers.wait_for_occupied_port = self.__fake_wait_for_occupied_port
        self._lost_responses = {}

    def __fake_wait_for_occupied_port(self, host, port):
        return

    def start(self):
        cherrypy.config.update("units/webui/server.conf")
        #cherrypy.config.update({ "environment": "embedded" })

        conf = {
            '/':{
                'tools.staticdir.root': os.path.abspath(os.getcwd()),
                'tools.staticdir.on': True,
                'tools.staticdir.dir': 'units/webui/html'
            }
        }
        cherrypy.quickstart(self, '/', conf)

    ''' ############################################
    '''
    @cherrypy.expose
    def default(self, *args,**kwargs):
        raise cherrypy.HTTPRedirect("/index.html")

    @cherrypy.expose
    def halt(self):
        cherrypy.engine.exit()

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def request(self):
        channel = tools.gen_token()
        message = cherrypy.request.json
        message['channel'] = channel
        message['src'] = self._webui.name

        self._webui.register_resp(channel)
        self._webui.dispatch(message)

        self._lost_responses[channel] = 0

        return {'error':'success', 'channel':channel}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def response(self):
        data = cherrypy.request.json
        print('[webui.response] {0}'.format(data))
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

        return {'error':'success', 'responses':responses, 'channels':list(_responses.keys())}