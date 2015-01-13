
import time

from units.modules import tools
from units.modules.unit import Unit


class HTTP(Unit):

    name = 'http'
    protocols = ['http', 'https']

    def __init__(self, core):
        super(HTTP, self).__init__(core)

        #self.stages = {'initial':self.initial_stage,}

    def start(self):
        print('[http] Starting')
        self.register()
        self.add_cmd_handler('digest', self.digest)

    ''' ############################################
        Command handlers
    '''
    def digest(self, message):
        task = message['params']['task']

        if task['stage'] == 'initial':
            message = {'dst':message['src'], 'src':self.name,
                       'cmd':'set', 'params':{'values':{'task':{'id':task['id'], 'stage':'crawling'}}, 'table':'task'}}
            self.dispatch(message)

        elif task['stage'] == 'forcing':
            print('[i] Sync Digest Message - {0}'.format(message))
            for c in range(1, 7):
                print('[http] Waiting cicle {0}'.format(c))
                time.sleep(4)

        elif task['stage'] == 'crawling':
            pass

        else:
            print('[e] http.digest: unknown stage {0}'.format(task['stage']))

        return {'status':'done'}

