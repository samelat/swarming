
import time
from threading import Lock

from units.tasker.orm import *


class Logic:

    def __init__(self, tasker, db_mgr):
        self._tasker = tasker
        self._db_mgr = db_mgr
        self._cycle_delay = 10
        self._units = {}


    def _get_protocol_units(self):
        protocol_units = {}

        self._db_mgr.session_lock.acquire()

        for unit in self._db_mgr.session.query(Unit).all():
            for protocol in unit.protocols:
                protocol_units[protocol.name] = unit.name

        self._db_mgr.session_lock.release()

        print('[tasker.protocol_units] {0}'.format(protocol_units))

        return protocol_units


    def _get_new_tasks(self):

        self._db_mgr.session_lock.acquire()

        resources = self._db_mgr.session.query(Resource).\
                                         filter(~Task.resource.has(Resource.id)).\
                                         all()

        ''' For each resource does not has a Task, we create a new one if there
            is a Unit that support its protocol.
        '''
        timestamp = self._db_mgr.timestamp()
        tasks = [Task(resource=rsrc, timestamp=timestamp)
                 for rsrc in resources if rsrc.service.protocol.name in self._units]
        if tasks:
            self._db_mgr.session.add_all(tasks)
            self._db_mgr.session.commit()

        json_tasks = [task.to_json() for task in tasks]

        self._db_mgr.session_lock.release()

        for json_task in json_tasks:
            print('[tasker.new_task] {0}'.format(json_task))

        return json_tasks

    '''

    '''
    def __get_stopped_tasks(self, stage):
        json_tasks = []

        self._db_mgr.session_lock.acquire()

        tasks = self._db_mgr.session.query(Task).\
                                     filter_by(state = 'stopped').\
                                     filter(Task.stage.like(stage + '%')).all()

        if tasks:
            for task in tasks:
                task.state = 'running'
                json_tasks.append(task.to_json())
            self._db_mgr.session.commit()

        self._db_mgr.session_lock.release()

        return json_tasks

    '''

    '''
    def _get_initial_tasks(self):
        json_tasks = self.__get_stopped_tasks('initial')

        for json_task in json_tasks:
            print('[tasker.initial_task] {0}'.format(json_task))

        return json_tasks

    '''

    '''
    def _get_forcing_tasks(self):
        json_tasks = self.__get_stopped_tasks('forcing')

        for json_task in json_tasks:
            print('[tasker.forcing_task] {0}'.format(json_task))

        return json_tasks

    '''

    '''
    def _get_crawling_tasks(self):
        json_tasks = self.__get_stopped_tasks('crawling')

        for json_task in json_tasks:
            print('[tasker.crawling_task] {0}'.format(json_task))

        return json_tasks

    '''

    '''
    def _check_waiting_tasks(self):
        return []


    ''' This method change de state field of every task
        to set them to 'stopped'
    '''
    def _restart_tasks(self):
        self._db_mgr.session_lock.acquire()
        tasks = self._db_mgr.session.query(Task).filter(Task.state != 'stopped',
                                                        Task.state != 'complete').all()
        for task in tasks:
            task.state = 'stopped'
        self._db_mgr.session.commit()
        self._db_mgr.session_lock.release()


    def start(self):

        print('[tasker] starting logic')
        self._restart_tasks()

        while not self._tasker.halt:

            print('#######################################################')
            print('[tasker] logic main loop')
            # Get units per protocol
            self._units = self._get_protocol_units()

            self._check_waiting_tasks()

            tasks = []
            tasks.extend(self._get_new_tasks())
            tasks.extend(self._get_initial_tasks())
            tasks.extend(self._get_forcing_tasks())
            tasks.extend(self._get_crawling_tasks())

            time.sleep(self._cycle_delay)

            #continue

            # Create a message for each task to do.
            for task in tasks:
                protocol = task['resource']['service']['protocol']['name']
                message = {'dst':self._units[protocol], 'src':'tasker', 'async':False,
                           'cmd':'consume', 'params':{'task':task}}

                schedule_msg = {'dst':'core', 'src':'tasker', 'cmd':'schedule', 'params':{}}
                schedule_msg['params']['message'] = message

                response = self._tasker.core.dispatch(schedule_msg)

                print('[logic] Schedule response: {0}'.format(response))
