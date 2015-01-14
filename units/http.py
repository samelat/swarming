
import time

from units.modules import tools
from units.modules.light_unit import LightUnit


class HTTP(LightUnit):

    name = 'http'
    protocols = ['http', 'https']

    def __init__(self, core):
        super(HTTP, self).__init__(core)

    def start(self):
    	super(HTTP, self).start()
    	self.add_stage_hanlder('initial', self.http_initial_stage)

    ''' ############################################
        Command & Stage handlers
    '''
    def http_initial_stage(self, message):
    	print('HTTP Initial Stage method')
