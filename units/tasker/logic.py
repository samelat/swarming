
import time
import json
from threading import Lock
from sqlalchemy import func

from units.tasker.orm import *


class Logic:

    def __init__(self, tasker, db_mgr):
        self._tasker = tasker
        self._db_mgr = db_mgr
        self._cycle_delay = 10
        self._units = {}

        # Forcing Dictionary
        self.dictionary_limit = 3


    def _schedule_task(self, task):
        protocol = task['task']['protocol']
        message = {'dst':self._units[protocol], 'src':'tasker', 'async':False,
                   'cmd':'consume', 'params':task}

        schedule_msg = {'dst':'core', 'src':'tasker', 'cmd':'schedule', 'params':{}}
        schedule_msg['params']['message'] = message

        return self._tasker.core.dispatch(schedule_msg)


    ''' #################################################
    
        #################################################
    '''
    def _get_protocol_units(self):
        protocol_units = {}

        self._db_mgr.session_lock.acquire()

        for unit in self._db_mgr.session.query(Unit).all():
            protocol_units[unit.protocol] = unit.name

        self._db_mgr.session_lock.release()

        print('[tasker.protocol_units] {0}'.format(protocol_units))

        return protocol_units


    ''' #################################################

        #################################################
    '''
    def _ready_tasks(self):

        self._db_mgr.session_lock.acquire()

        crawling_tasks = self._db_mgr.session.query(Task).\
                                              filter_by(state = 'ready').\
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

                response = self._schedule_task(_task)
                print('[logic.crawling_task] Schedule response: {0}'.format(response))
            self._db_mgr.session.commit()

        self._db_mgr.session_lock.release()


    ''' TODO: ###########################################
        Este metodo deberia buscar todas las relaciones
        faltantes entre tablas como 'dictionary' y las
        'tasks' que las utilicen, para crear asi nuevos
        mensajes de trabajo a realizar.
        #################################################
    '''
    def _forcing_dictionary_tasks(self):

        self._db_mgr.session_lock.acquire()

        running_subtasks = self._db_mgr.session.query(DictionaryTask).\
                                                filter_by(state = 'running').\
                                                all()

        running_tasks = set()
        self._tasker._resp_lock.acquire()
        for subtask in running_subtasks:
            if subtask.channel in self._tasker._responses:
                del(self._tasker._responses[subtask.channel])
                subtask.state = 'complete'
            else:
                running_tasks.add(subtask.task_id)
        self._tasker._resp_lock.release()

        self._db_mgr.session.commit()

        #self._db_mgr.session_lock.release()

        #################################################################
        #################################################################
        
        forcing_tasks = self._db_mgr.session.query(Task).\
                                     filter((Task.state == 'running')|
                                            (Task.state == 'ready')).\
                                     filter_by(stage = 'forcing.dictionary').\
                                     all()

        if forcing_tasks:

            '''
            last_dict_entry = self._db_mgr.session.query(func.max(Dictionary.id),
                                                         Dictionary.username,
                                                         Dictionary.password).one()
            if not last_dict_entry:
                return []
            '''

            for task in forcing_tasks:
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

                count = 0
                current_entry = None
                dictionary = {'usernames':set(), 'passwords':set(), 'pairs':set()}
                while True:

                    last_entry = current_entry

                    if index == current:
                        current_entry = self._db_mgr.session.query(Dictionary).\
                                                             order_by(Dictionary.id.asc()).\
                                                             filter(Dictionary.id > current).first()
                        if not current_entry:
                            print('[forcing.dictionary] {0}'.format(dictionary))
                            dictionaries.append(dictionary)
                            break

                        index = 0
                        current = current_entry.id

                    else:
                        current_entry = self._db_mgr.session.query(Dictionary).\
                                                             filter_by(id = current).one()


                    if last_entry and\
                       ((current_entry.password == None) ^ (last_entry.password == None)) and\
                       (dictionary['passwords'] and dictionary['usernames']):
                            print('##############################################')
                            print('[forcing.dictionary] {0}'.format(dictionary))
                            dictionaries.append(dictionary)
                            dictionary = {'usernames':set(), 'passwords':set(), 'pairs':set()}

                    ####################################

                    # It's a password
                    if current_entry.username == None:
                        
                        usernames = self._db_mgr.session.query(Dictionary.id, Dictionary.username).\
                                                         filter(Dictionary.id > index,
                                                                Dictionary.id < current,
                                                                Dictionary.password == None).all()

                        dictionary['passwords'].add(current_entry.password)
                        dictionary['usernames'].update([usr for uid, usr in usernames])

                        count += len(usernames)

                    # It's a username
                    elif current_entry.password == None:
                        # The password's ID will be used in a futer limitation in the number of results.
                        passwords = self._db_mgr.session.query(Dictionary.id, Dictionary.password).\
                                                         filter(Dictionary.id > index,
                                                                Dictionary.id < current,
                                                                Dictionary.username == None).all()

                        dictionary['usernames'].add(current_entry.username)
                        dictionary['passwords'].update([pwd for pid, pwd in passwords])

                        count += len(passwords)

                    # It's a pair
                    else:
                        #dictionary['usernames'].add(current_entry.username)
                        count += 1

                    index = current

                    if count > self.dictionary_limit:
                        print('[forcing.dictionary] limited - {0}'.format(dictionary))
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
                    complements.update(json.loads(dependence.complements.values))
                    dependence = dependence.dependence

                _task = {'task':task.to_json(), 'dictionaries':_dictionaries}
                if complements:
                    _task['complements'] = complements

                response = self._schedule_task(_task)
                print('[logic] Schedule response: {0}'.format(response))

                new_subtask = DictionaryTask(index=index, current=current,
                                             channel=response['channel'],
                                             state='running', timestamp=self._db_mgr.timestamp())
                new_subtask.task = task
                self._db_mgr.session.add(new_subtask)

            # ???????????????????
            self._db_mgr.session.commit()

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
                                     filter(Task.state != 'stopped', Task.stage != 'complete').\
                                     all()
        for task in tasks:
            task.state = 'ready'
        self._db_mgr.session.commit()
        self._db_mgr.session_lock.release()


    ''' #################################################

        #################################################
    '''
    def start(self):

        print('[tasker] starting logic')
        self._restart_tasks()

        while not self._tasker.halt:

            print('#######################################################')
            print('[tasker] logic main loop')
            # Get units per protocol
            self._units = self._get_protocol_units()

            self._waiting_tasks()

            self._ready_tasks()
            self._forcing_dictionary_tasks()

            time.sleep(self._cycle_delay)
