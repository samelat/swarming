
import os
import cherrypy
from cherrypy.process import servers

from units.modules import tools


class APIService:

    def __init__(self, webui):
        self._webui = webui
        # cherrypy fix
        servers.wait_for_occupied_port = self.__fake_wait_for_occupied_port

    def __fake_wait_for_occupied_port(self, host, port):
        return

    def start(self):
        cherrypy.config.update("units/webui/server.conf")
        cherrypy.config.update({ "environment": "embedded" })

        conf = {
            '/':{
                'tools.staticdir.root': os.path.abspath(os.getcwd()),
                'tools.staticdir.on': True,
                'tools.staticdir.dir': './units/webui/html'
            }
        }
        cherrypy.quickstart(self, '/', conf)

    ''' ############################################
    '''
    @cherrypy.expose
    def halt(self):
        cherrypy.engine.exit()

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def request(self):
        channel_id = tools.gen_token()
        message = cherrypy.request.json
        message['id'] = channel_id
        message['src'] = self._webui.name

        self._webui.register_resp(channel_id)
        self._webui.dispatch(message)

        return {'error':'success', 'id':channel_id}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def response(self):
        data = cherrypy.request.json
        print('/RESPONSE {0}'.format(data))
        responses = self._webui.get_responses(data['channels'])

        print("RESPONSES: {0}".format(responses))
        return {'error':'success', 'responses':responses, 'channels':list(responses.keys())}