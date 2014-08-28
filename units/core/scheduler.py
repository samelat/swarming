

class Scheduler:

    def __init__(self, core):
        self._core = core

        ''' TODO: It is better if we take the list of
            modules to load from a config file or something
            like that (do not hardcode them).
        '''
        self._units = {}
        self._tasks = {1,2,3,4}

    def start(self):
        print('[core] Starting all standard units...')
        for uname in self._units:
            for tid in self._units[uname]:
                self._units[uname][tid].start()
            #map(lambda u: u.start(), self._units[uname].values())
        print('[core] done')
        while True:
            continue

    def halt(self):
        print('[core] Broadcasting "halt" message...')
        '''
        for unit_name in self.units.items():
            cmsg = message.copy()
            cmsg['dst'] = unit_name
            print('[core] Sending from "halt" message: {0}'.format(cmsg))
            unit.dispatch(cmsg)
            unit.wait()
        '''
    
    def add_unit(self, unit):
        # Unit name, Task ID
        uname, tid = unit.name()

        if uname not in self._units:
            self._units[uname] = {0:unit}
        else:
            tid = self._tasks.pop()
            self._units[uname][tid] = unit

        return (uname, tid)

    def forward(self, message):
        uname, tid = message['dst']
        try:
            self._units[uname][tid].dispatch(message)
        except:
            pass
            # TODO: We could generate a error here, informing that
            #       the dst module does not exist.


    ''' ############################################
        Commands
    '''
    def schedule(self, message):
        print('[core] Scheduling: {0}'.format(message))