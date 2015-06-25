
import time
import json
from threading import Lock
from sqlalchemy import func

from units.engine.orm import *
from modules.keyspace import KeySpace


class Tasker:

    def __init__(self, engine):
        self._engine = engine
        self._db_mgr = ORM()
        self._cycle_delay = 10
        self._units = {}

        self._cracking_dictionary_channels = {}
        self._ready_task_channels = {}

        # Forcing Dictionary
        self.dictionary_limit = 200


    def _dispatch_task(self, task):
        protocol = task['task']['protocol']
        message = {'dst':self._units[protocol], 'src':'engine', 'async':False,
                   'cmd':'consume', 'params':task}

        return self._engine.core.dispatch(message)


    ''' #################################################
    
        #################################################
    '''
    def _get_protocol_units(self):
        protocol_units = {}

        self._db_mgr.session_lock.acquire()

        for unit in self._db_mgr.session.query(Unit).all():
            protocol_units[unit.protocol] = unit.name

        self._db_mgr.session_lock.release()

        print('[engine.protocol_units] {0}'.format(protocol_units))

        return protocol_units


    ''' #################################################

        #################################################
    '''
    def _control_dictionary(self):
        # We are going to update all entries without weight
        # First, usernames and password
        self._db_mgr.session_lock.acquire()
        entries = self._db_mgr.session.query(Dictionary).\
                                       filter((Dictionary.type >= 3) &\
                                              (Dictionary.type <= 5) &\
                                              (Dictionary.weight == 1)).all()
        print('[tasker] entries: {0}'.format(entries))
        for entry in entries:
            mask = entry.username + entry.password
            entry.weight = len(KeySpace(mask, json.loads(entry.charsets)))
        self._db_mgr.session.commit()
        self._db_mgr.session_lock.release()


    ''' #################################################

        #################################################
    '''
    def _ready_tasks(self):

        self._db_mgr.session_lock.acquire()

        self._engine._resp_lock.acquire()
        for channel in list(self._ready_task_channels.keys()):
            if channel in self._engine._responses:
                task_id = self._ready_task_channels[channel]
                task = self._db_mgr.session.query(Task).\
                                            filter_by(id=task_id).first()
                task.state = 'complete'
                self._db_mgr.session.commit()

        self._engine._resp_lock.release()

        #################################################################
        #################################################################

        crawling_tasks = self._db_mgr.session.query(Task).\
                                              filter_by(state = 'ready').\
                                              filter(Task.protocol == Unit.protocol).\
                                              filter(Task.stage.like('crawling')|Task.stage.like('initial')).\
                                              all()

        if crawling_tasks:
            for task in crawling_tasks:
                task.state = 'running'

                complements = {}
                dependence = task.dependence
                while dependence:
                    complements.update(json.loads(dependence.complement.values))
                    dependence = dependence.dependence

                _task = {'task':task.to_json()}
                if complements:
                    _task['complements'] = complements

                response = self._dispatch_task(_task)
                print('[tasker.crawling_task] Dispatch response: {0}'.format(response))

                if response['status'] < 0:
                    task.state = 'stopped'
                elif task.stage != 'initial':
                    self._ready_task_channels[response['channel']] = task.id

            self._db_mgr.session.commit()

        self._db_mgr.session_lock.release()


    ''' #################################################

        #################################################
    '''
    def _cracking_dictionary_tasks(self):

        self._db_mgr.session_lock.acquire()

        running_tasks = set()
        self._engine._resp_lock.acquire()
        for channel in list(self._cracking_dictionary_channels.keys()):
            subtask_id, task_id, count = self._cracking_dictionary_channels[channel]
            if channel in self._engine._responses:
                response = self._engine._responses[channel]
                del(self._engine._responses[channel])
                del(self._cracking_dictionary_channels[channel])
                subtask = self._db_mgr.session.query(DictionaryTask).\
                                               filter_by(id=subtask_id).first()
                subtask.state = 'complete'

                task = self._db_mgr.session.query(Task).\
                                            filter_by(id=task_id).first()
                task.done += count
            else:
                running_tasks.add(task_id)
        self._engine._resp_lock.release()

        self._db_mgr.session.commit()

        #################################################################
        #################################################################
        
        cracking_tasks = self._db_mgr.session.query(Task).\
                                              filter_by(stage = 'cracking.dictionary').\
                                              filter(Task.protocol == Unit.protocol).\
                                              filter((Task.state == 'running')|
                                                     (Task.state == 'ready')).\
                                              all()

        if cracking_tasks:

            for task in cracking_tasks:
                dictionaries = []

                # This is only to update the task's state
                if task.id not in running_tasks:
                    task.state = 'ready'

                # get last dictionary_task
                last_subtask = self._db_mgr.session.query(DictionaryTask).\
                                                    order_by(DictionaryTask.timestamp.desc()).\
                                                    filter_by(task_id = task.id).\
                                                    first()

                # TODO: I have to restrict the number of tasks that will be generated.
                if not last_subtask:
                    index = current = 0
                else:
                    index = last_subtask.index
                    current = last_subtask.current

                # Update remaining Work (+3 is the offset between each plain type and mask type)
                # TODO: filter by task_id too
                weights = []
                for _type in [0, 1, 2]:
                    weights[_type] = self._db_mgr.session.query(func.sum(Dictionary.weight)).\
                                                          filter((Dictionary.type == _type) |\
                                                                 (Dictionary.type == _type+3)).first()[0]
                    if weights[_type] == None:
                        weights[_type] = 0

                task.total = (weights[0] * weights[1]) + weights[3]

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

                count = 0
                current_entry = None
                ids = {'usernames':set(), 'passwords':set(), 'pairs':set()}
                dictionary = {'usernames':[], 'passwords':[], 'pairs':[]}
                while True:

                    # last_entry is only to control when current_entry has changed from
                    # username to password or vice versa
                    last_entry = current_entry

                    if index == current:
                        current_entry = self._db_mgr.session.query(Dictionary).\
                                                             order_by(Dictionary.id.asc()).\
                                                             filter(Dictionary.id > current).first()
                        if not current_entry:
                            print('[cracking.dictionary] {0}'.format(dictionary))
                            dictionaries.append(dictionary)
                            break

                        index = 0
                        current = current_entry.id

                    else:
                        current_entry = self._db_mgr.session.query(Dictionary).\
                                                             filter_by(id = current).one()

                    # Reset dictionary?
                    dict_breakpoints = list(itertools.product([0, 3],[1, 4]))
                    dict_breakpoints.extend(itertools.product([1, 4],[0, 3]))
                    if last_entry and\
                       ((current_entry.type, last_entry.type) in dict_breakpoints) and\
                       (ids['passwords'] and ids['usernames']):
                            print('##############################################')
                            print('[cracking.dictionary] {0}'.format(dictionary))
                            dictionaries.append(dictionary)
                            ids = {'usernames':set(), 'passwords':set(), 'pairs':set()}
                            dictionary = {'usernames':[], 'passwords':[], 'pairs':[]}

                    ####################################

                    # It's a username
                    if current_entry.type == 0:
                        # The password's ID will be used in a futer limitation in the number of results.
                        passwords = self._db_mgr.session.query(Dictionary.id, Dictionary.password).\
                                                         filter(Dictionary.id > index,
                                                                Dictionary.id < current,
                                                                Dictionary.type == 1).\
                                                         order_by(Dictionary.id.asc()).\
                                                         limit(10).all()

                        dictionary['usernames'].add(current_entry.username)
                        dictionary['passwords'].update([pwd for pid, pwd in passwords])

                        if passwords:
                            index = passwords[-1][0]
                        else:
                            index = current
                        count += len(passwords)

                    # It's a password
                    elif current_entry.type == 1:
                        
                        usernames = self._db_mgr.session.query(Dictionary.id, Dictionary.username).\
                                                         filter(Dictionary.id > index,
                                                                Dictionary.id < current,
                                                                Dictionary.type == 0).\
                                                         order_by(Dictionary.id.asc()).\
                                                         limit(10).all()

                        dictionary['passwords'].add(current_entry.password)
                        dictionary['usernames'].update([usr for uid, usr in usernames])

                        if usernames:
                            index = usernames[-1][0] # The last ID
                        else:
                            index = current
                        count += len(usernames)

                    # It's a pair
                    else:
                        pair = (current_entry.username, current_entry.password)
                        dictionary['pairs'].add(pair)
                        count += 1
                        index = current

                    if count > self.dictionary_limit:
                        print('[cracking.dictionary] limited - {0}'.format(dictionary))
                        dictionaries.append(dictionary)
                        break

                    ####################################

                if not count:
                    continue

                task.state = 'running'

                _dictionaries = []
                for dictionary in dictionaries:
                    _dictionaries.append({'usernames':list(dictionary['usernames']),
                                          'passwords':list(dictionary['passwords']),
                                          'pairs':list(dictionary['pairs'])})

                complements = {}
                dependence = task.dependence
                while dependence:
                    complements.update(json.loads(dependence.complement.values))
                    dependence = dependence.dependence

                _task = {'task':task.to_json(), 'dictionaries':_dictionaries}
                if complements:
                    _task['complements'] = complements

                response = self._dispatch_task(_task)
                print('[tasker] Dispatch response: {0}'.format(response))

                new_subtask = DictionaryTask(index=index, current=current,
                                             timestamp=self._db_mgr.timestamp())
                
                new_subtask.task = task
                self._db_mgr.session.add(new_subtask)
                self._db_mgr.session.commit()

                self._cracking_dictionary_channels[response['channel']] = (new_subtask.id, task.id, count)

        self._db_mgr.session_lock.release()


    ''' #################################################

        #################################################
    '''
    def _waiting_tasks(self):
        self._db_mgr.session_lock.acquire()

        waiting_tasks = self._db_mgr.session.query(Task).\
                                             filter(Task.state != 'stopped', 
                                                    Task.stage.like('waiting.%')).\
                                             all()
        if not waiting_tasks:
            self._db_mgr.session_lock.release()
            return

        for task in waiting_tasks:
            stage = task.stage.split('.')

            # waiting.dependence
            if (stage[1] == 'dependence') and (task.dependence.complement):
                task.stage = '.'.join(stage[2:])

            # waiting.time
            elif stage[1] == 'time':
                if int(stage[2]) < (self._db_mgr.timestamp() - task.timestamp)/1000:
                    task.stage = '.'.join(stage[3:])

        self._db_mgr.session.commit()

        self._db_mgr.session_lock.release()


    ''' #################################################
        This method change de state field of every task
        to set them to 'stopped'
        #################################################
    '''
    def _restart_tasks(self):
        self._db_mgr.session_lock.acquire()
        tasks = self._db_mgr.session.query(Task).\
                                     filter(Task.state != 'stopped', Task.state != 'complete').\
                                     all()
        for task in tasks:
            task.state = 'ready'
            if not task.stage.startswith('cracking'):
                task.done = 0
                task.total = 0

        subtasks = self._db_mgr.session.query(DictionaryTask).\
                                        filter(DictionaryTask.state != 'complete').\
                                        all()
        for subtask in subtasks:
            self._db_mgr.session.delete(subtask)

        self._db_mgr.session.commit()
        self._db_mgr.session_lock.release()


    ''' #################################################

        #################################################
    '''
    def start(self):

        print('[engine] starting logic')
        self._restart_tasks()

        while not self._engine.halt:

            print('#######################################################')
            print('[BBBBBBBBBB] {0}'.format(self._db_mgr.session_lock))
            print('[engine] Tasker main loop')
            # Get units per protocol
            self._units = self._get_protocol_units()

            self._control_dictionary()

            self._waiting_tasks()

            self._ready_tasks()
            self._cracking_dictionary_tasks()

            time.sleep(self._cycle_delay)
