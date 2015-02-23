
from multiprocessing import Process

from units.modules.unit import Unit
from units.modules.messenger import Messenger

from units.webui.api_service import APIService


class WebUI(Unit):

    name = 'webui'

    def __init__(self, core):
        super(WebUI, self).__init__(core)
        self._process = None
        self._messenger = Messenger(self)
        self._api_service = APIService(self)

    ''' ############################################
    '''
    def _launcher(self):
        #self._messenger.start()
        self._api_service.start()


    ''' ############################################
    '''
    def dispatch(self, message):
        return self._messenger.push(message)

    def wait(self):
        self._process.join()

    def start(self):
        print('[webui] Starting')
        self._process = Process(target=self._launcher)
        self._process.start()
