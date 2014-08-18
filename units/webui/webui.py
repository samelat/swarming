
from multiprocessing import Process

from units.modules import tools
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
        self._messenger.start(True)
        self._api_service.start()

    ''' ############################################
    '''
    def halt(self, message):
        print('[webapi] Halting service ...')
        self._halt = True

    def response(self, message):
        print('[webapi] Response message: {0}'.format(message))

    ''' ############################################
    '''
    def dispatch(self, message):
        self._messenger.push(message)

    def wait(self):
        self._process.join()

    def start(self):
        self._process = Process(target=self._launcher)
        self._process.start()
