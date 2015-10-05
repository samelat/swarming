
import json
import cherrypy

from units.engine.orm import *
#from units.engine.webui.uiapi.csv import CSV


class FilesAPI:

    exposed = True

    def __init__(self):
        self.orm = ORM()
        #self.file_parsers = {'csv': CSV}

    @cherrypy.tools.json_out()
    def POST(self, file, json_params):
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
