
from units.engine.orm import *

''' 
    {
        'usernames':[
            {'type':0, 'username':'guess'},
            {'type':3, 'username':'19?1?d', 'charset':{'?1':'56789'}}
        ], 

        'passwords':[...],

        'pairs':[
            [{'type':2, 'username':'user1', 'password':'pass1'},
             {'type':5, 'username':'root' , 'password':'root?d?d?1', 'charset':{'?1':'AB'}},
        ]
    }
'''
class WorkPlanner:

    def __init__(self, orm, task, work_limit):
        self.orm = orm
        self.task = task
        self.work_limit = work_limit

        self.work = None
        #self.weights = []
        #self.weights = [0]

        self.index = 0
        self.current = 0

        self.cycles = []
        #self.dictionary_cache = {}

    '''

    '''
    def get_work_weight(self):
        weight = 0
        for cycle in self.cycles:
            weight += sum([e.weight for e in cycle['usernames'].values()]) * sum([e.weight for e in cycle['passwords'].values()])
            if 'pairs' in cycle:
                weight += sum([e.weight for e in cycle['pairs'].values()])

        return weight

    '''

    '''
    def get_cycle_entries(self, types, weight_edge):

        total_weight = 0
        chunk_size = 10
        entries = {}
        # The password's ID will be used in a futer limitation in the number of results.
        
        _entries = self.orm.session.query(Dictionary).\
                                    filter(Dictionary.id > self.index,
                                           Dictionary.id < self.current).\
                                    filter((Dictionary.type == types[0]) |\
                                           (Dictionary.type == types[1])).\
                                    order_by(Dictionary.id.asc()).\
                                    limit(chunk_size).all()

        while _entries:
            entry = _entries.pop(0)
            print('[ids] {0}'.format(entry.id))
            entries[entry.id] = entry
            self.index = entry.id
            total_weight += entry.weight
            if total_weight > weight_edge:
                break

        if not _entries:
            self.index = self.current

        return entries

    ''' #####################################################

        #####################################################
    '''
    def merge_cycles(self, cycle):

        if self.cycles:
            if cycle['usernames'].keys() == self.cycles[-1]['usernames'].keys():
                self.cycles[-1]['passwords'].update(cycle['passwords'])
                self.cycles[0]['pairs'].update(cycle['pairs'])
                return

            elif cycle['passwords'].keys() == self.cycles[-1]['passwords'].keys():
                self.cycles[-1]['usernames'].update(cycle['usernames'])
                self.cycles[0]['pairs'].update(cycle['pairs'])
                return

        self.cycles.append(cycle)

    ''' #####################################################

        #####################################################
    '''
    def get_pending_work(self):

        # get last dictionary_task
        last_work = self.orm.session.query(DictionaryTask).\
                                           order_by(DictionaryTask.timestamp.desc()).\
                                           filter_by(task_id = self.task.id).\
                                           first()
        if last_work:
            self.index = last_work.index
            self.current = last_work.current

        current_entry = None
        if self.current > self.index:
            # Continue previous iteration
            current_entry = self.orm.session.query(Dictionary).\
                                             filter_by(id = self.current).first()

        while self.get_work_weight() < self.work_limit:

            print('[weight] {0}'.format(self.get_work_weight()))

            if self.index == self.current:
                # last_entry is only to control when current_entry has changed from
                # username to password or vice versa
                #last_entry = current_entry

                current_entry = self.orm.session.query(Dictionary).\
                                                 order_by(Dictionary.id.asc()).\
                                                 filter(Dictionary.id > self.current).first()
                if not current_entry:
                    break

                self.index = 0
                self.current = current_entry.id

                #self.dictionary_cache[current_entry.id] = current_entry

            #### Start new Cycle ####
            cycle = {'usernames':{}, 'passwords':{}, 'pairs':{}}

            ####################################

            # This weight limit is not precise, but works
            weight_edge = (self.work_limit - self.get_work_weight())/current_entry.weight

            # current is a username
            if current_entry.type in [0, 3]:
                cycle['usernames'][current_entry.id] = current_entry
                entries = self.get_cycle_entries([1, 4], weight_edge)
                cycle['passwords'] = entries

            # current is a password
            elif current_entry.type in [1, 4]:
                cycle['passwords'][current_entry.id] = current_entry
                entries = self.get_cycle_entries([0, 3], weight_edge)
                cycle['usernames'] = entries

            # current is a pair
            else:
                cycle['pairs'][current_entry.id] = current_entry
                self.index = self.current

            ####################################

            print('[!] current: {0} - index: {1}'.format(self.current, self.index))
            print('[cycles] {0}'.format(cycle))

            self.merge_cycles(cycle)

        #self.update_dictionary_ids(ids)

        print('[cycles] {0}'.format(self.cycles))
        print('[weight] {0}'.format(self.get_work_weight()))

        #print(self.get_weight())

        if not self.cycles:
            return None

        dictionaries = []
        for cycle in self.cycles:
            dictionary = {}
            dictionary['usernames'] = [entry.to_json() for entry in cycle['usernames'].values()]
            dictionary['passwords'] = [entry.to_json() for entry in cycle['passwords'].values()]
            if cycle['pairs']:
                dictionary['pairs'] = [entry.to_json() for entry in cycle['pairs'].values()]

            dictionaries.append(dictionary)

        self.work = DictionaryTask(index=self.index, current=self.current,
                                   timestamp=self.orm.timestamp())
        
        self.work.task = self.task
        self.orm.session.add(self.work)
        self.orm.session.commit()

        return {'dictionaries':dictionaries}

