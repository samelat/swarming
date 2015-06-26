
from units.engine.orm import *


class WorkPlanner:

    def __init__(self, orm, task, work_limit):
        self.orm = orm
        self.task = task
        self.work_limit = work_limit

        self.work = None
        self.weights = {'usernames':0, 'passwords':0, 'pairs':0}

        self.index = 0
        self.current = 0

        self.dictionary_ids = []
        self.dictionary_cache = {}

    '''

    '''
    def get_weight(self):
        return (self.weights['usernames'] * self.weights['passwords']) + self.weights['pairs']

    '''

    '''
    def get_remaining_ids(self, field):

        chunk_size = 10

        if field == 'usernames':
            types = [1, 4]
        else:
            types = [0, 3]

        # The password's ID will be used in a futer limitation in the number of results.
        ids = set()
        entries = self.orm.session.query(Dictionary).\
                                     filter(Dictionary.id > self.index,
                                            Dictionary.id < self.current).\
                                     filter((Dictionary.type == types[0]) |\
                                            (Dictionary.type == types[1])).\
                                     order_by(Dictionary.id.asc()).\
                                     limit(chunk_size).all()

        consumed = 0
        while entries:
            entry = entries.pop(0)
            ids.add(entry.id)
            self.index = entry.id
            self.weights[field] += entry.weight
            if self.get_weight() >= self.work_limit:
                break

        if not entries:
            self.index = self.current

        return ids


    def update_dictionary_ids(self, ids):
        if not self.dictionary_ids:
            self.dictionary_ids.append(ids)
            return

        if ids['usernames'] == self.dictionary_ids[-1]['usernames']:
            self.dictionary_ids[-1]['passwords'].update(ids['passwords'])

        elif ids['passwords'] == self.dictionary_ids[-1]['passwords']:
            self.dictionary_ids[-1]['usernames'].update(ids['usernames'])
            
        else:
            self.dictionary_ids.append(ids)

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
                                             filter_by(id = current).first()
            self.dictionary_cache[current_entry.id] = current_entry

        ids = {'usernames':set(), 'passwords':set()}

        while self.get_weight() < self.work_limit:

            print('[!] current: {0} - index: {1}'.format(self.current, self.index))
            print('[cracking.dictionary] {0}'.format(ids))

            if self.index == self.current:
                # last_entry is only to control when current_entry has changed from
                # username to password or vice versa
                #last_entry = current_entry

                current_entry = self.orm.session.query(Dictionary).\
                                                 order_by(Dictionary.id.asc()).\
                                                 filter(Dictionary.id > self.current).first()
                if not current_entry:
                    break

                self.dictionary_cache[current_entry.id] = current_entry
                
                self.update_dictionary_ids(ids)
                ids = {'usernames':set(), 'passwords':set()}

                self.index = 0
                self.current = current_entry.id

            ####################################

            # current is a username
            if current_entry.type in [0, 3]:
                field_ids = self.get_remaining_ids('usernames')
                ids['usernames'].update(field_ids)

            # current is a password
            elif current_entry.type in [1, 4]:
                field_ids = self.get_remaining_ids('passwords')
                ids['passwords'].update(field_ids)

            # current is a pair
            else:
                dictionary['pairs'].add(pair)
                self.index = self.current

            ####################################

        self.update_dictionary_ids(ids)

        print(self.dictionary_ids)

        print(self.get_weight())

        if not self.get_weight():
            return None

        '''
        _dictionaries = []
        for dictionary in dictionaries:
            _dictionaries.append({'usernames':list(dictionary['usernames']),
                                  'passwords':list(dictionary['passwords']),
                                  'pairs':list(dictionary['pairs'])})

        pending_work['task'] = task.to_json()

        self.work = DictionaryTask(index=index, current=current,
                                   timestamp=self._db_mgr.timestamp())
        
        self.subtask.task = task
        self.orm.session.add(self.work)
        self.orm.session.commit()

        return {'task':self.task.to_json(), 'dictionaries':dictionaries}
        '''

