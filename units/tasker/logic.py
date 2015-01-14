
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


    def _get_initial_tasks(self):
        self._db_mgr.session_lock.acquire()

        tasks = self._db_mgr.session.query(Task).\
                                     filter_by(stage = 'initial').all()

        json_tasks = [task.to_json() for task in tasks]

        self._db_mgr.session_lock.release()

        for json_task in json_tasks:
            print('[tasker.initial_task] {0}'.format(json_task))

        return json_tasks


    def _get_new_tasks(self):

        self._db_mgr.session_lock.acquire()

        resources = self._db_mgr.session.query(Resource).\
                                         filter(~Task.resource.has(Resource.id)).\
                                         all()

        ''' For each resource that not has a Task, we create a new one if there
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


    def _get_login_tasks(self):
        return []


    def _get_crawling_tasks(self):
        return []


    def _get_waiting_tasks(self):
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
        self._db_mgr.session_lock.release()

        


    def start(self):

        self._restart_tasks()

        while not self._tasker.halt:

            # Get units per protocol
            self._units = self._get_protocol_units()

            tasks = []
            tasks.extend(self._get_initial_tasks())
            tasks.extend(self._get_new_tasks())
            tasks.extend(self._get_login_tasks())

            time.sleep(self._cycle_delay)

            #continue

            # Create a message for each task to do.
            messages = []
            for task in tasks:
                protocol = task['resource']['service']['protocol']['name']
                message = {'dst':self._units[protocol], 'src':'tasker', 'async':False,
                           'cmd':'digest', 'params':{'task':task}}
                messages.append(message)

            # Create a schedule message for all pending task messages.
            if messages:
                schedule_msg = {'dst':'core', 'src':'tasker', 'cmd':'schedule', 'params':{}}
                schedule_msg['params']['messages'] = messages

                response = self._tasker.dispatch(schedule_msg)

            print('#######################################################')
            