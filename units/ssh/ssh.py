
from modules.light_unit import LightUnit


class SSH(LightUnit):

    name = 'ssh'
    protocols = {'ssh' :22}

    def __init__(self, core):
        super(SSH, self).__init__(core)

        self.stages['initial']  = self.ssh_initial_stage
        self.stages['crawling'] = self.ssh_crawling_stage
        self.stages['cracking.dictionary']  = self.ssh_cracking_stage
        

    ''' ############################################
        Command & Stage handlers
    '''
    def ssh_initial_stage(self, message):
        print('[ssh] Initial Stage method')

        # We return in 'updates' the self task values we want to change.
        values = {'stage':'cracking.dictionary', 'state':'ready'}

        return {'status':0, 'task':values}

    ''' 
    '''
    def ssh_cracking_stage(self, message):
        print('[ssh] Forcing Stage method')

        return {'status':0}

    ''' 
    '''
    def ssh_crawling_stage(self, message):
        print('[ssh] Crawling Stage method [Not yet implemented]')

        return {'status':0}
