
from modules.light_unit import LightUnit

from units.ssh import hperf_ssh

class SSH(LightUnit):

    name = 'ssh'
    protocols = {'ssh' : 22}

    def __init__(self, core):
        super(SSH, self).__init__(core)

        self.stages['initial']  = self.ssh_initial_stage
        self.stages['crawling'] = self.ssh_crawling_stage
        self.stages['cracking.dictionary']  = self.ssh_cracking_stage
        

    ''' ############################################
        Command & Stage handlers
    '''
    def ssh_initial_stage(self, message):
        #print('[ssh] Initial Stage method')
        
        self.set_knowledge({'task':self.task})

        return {'status':0}

    ''' ############################################
        Needed methods for cracking hperf module
    '''
    def ssh_success_callback(self, username, password):
        #print('[!] Login! username: {0} - password: {1}'.format(username, password))
        self.success({'username':username, 'password':password})

    def ssh_retry_callback(self, attempt):
        #print('[!] Retry - Attempt {0}'.format(attempt))
        if(attempt < 3):
            return True
        return False

    def ssh_cracking_stage(self, message):
       #print('[ssh] Forcing Stage method')

        for dictionary in message['params']['dictionaries']:
            cracker = hperf_ssh.SSH(self.ssh_success_callback,
                                    self.ssh_retry_callback,
                                    self.task['hostname'], self.task['port'])
            cracker.crack(**dictionary)

        return {'status':0}

    ''' ############################################
    '''
    def ssh_crawling_stage(self, message):
        #print('[ssh] Crawling Stage method [Not yet implemented]')

        return {'status':0}
