
import time
import json
import logging
from threading import Lock
from sqlalchemy import func

import logging

from units.engine.orm import *
from common.config import config
from common.keyspace import KeySpace

from units.engine.tasker.work_planner import WorkPlanner


class Tasker:

    def __init__(self, engine):
        self.logger = logging.getLogger(__name__)

        self._engine = engine

        self._db_mgr = ORM()
        self._cycle_delay = 10
        self._units = {}

        self._cracking_dictionary_channels = {}
        self._ready_task_channels = {}

        # Forcing Dictionary
        self.work_limit = 200

    def _dispatch_task(self, task):
        protocol = task['task']['protocol']
        message = {'dst': self._units[protocol], 'src': 'engine', 'async': False,
                   'cmd': 'consume', 'params': task}

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

        # print('[engine.protocol_units] {0}'.format(protocol_units))
        return protocol_units

    ''' #################################################
        #################################################
    '''
    def _control_dictionary(self):
        # We are going to update all entries without weight.
        # First, usernames and passwords
        self._db_mgr.session_lock.acquire()
        entries = self._db_mgr.session.query(Dictionary).filter((Dictionary.type >= 3) &
                                                                (Dictionary.type <= 5) &
                                                                (Dictionary.weight == 1)).all()

        # print('[tasker] entries: {0}'.format(entries))
        for entry in entries:
            mask = entry.username + entry.password
            entry.weight = len(KeySpace(mask, json.loads(entry.charsets)))
            # TODO: If weight is ==1, we have to change this entry type.
        self._db_mgr.session.commit()
        self._db_mgr.session_lock.release()

    ''' #################################################
        #################################################
    '''
    def _ready_tasks(self):

        # First we are going to handle responses.

        self._db_mgr.session_lock.acquire()

        self._engine._resp_lock.acquire()

        for channel in list(self._ready_task_channels.keys()):
            if channel in self._engine._responses:
                response = self._engine._responses[channel]
                task_id = self._ready_task_channels[channel]

                del(self._engine._responses[channel])
                del(self._ready_task_channels[channel])

                task = self._db_mgr.session.query(Task).filter_by(id=task_id).first()

                if response['status'] < 0:
                    task.state = 'error'
                    if 'error' in response:
                        task.description = response['error']

                self._db_mgr.session.commit()

        self._engine._resp_lock.release()

        #################################################################
        #################################################################

        crawling_tasks = self._db_mgr.session.query(Task).\
            filter_by(state='ready').\
            filter(Task.protocol == Unit.protocol).\
            filter(Task.stage.like('crawling') | Task.stage.like('initial')).\
            all()

        if crawling_tasks:
            for task in crawling_tasks:
                task.state = 'running'

                # Load all task's registers and dispatch the task
                registers = [json.loads(register) for register in task.registers]
                response = self._dispatch_task({'task': task.to_json(), 'registers': registers})

                if response['status'] < 0:
                    task.state = 'stopped'
                else:
                    self._ready_task_channels[response['channel']] = task.id

            self._db_mgr.session.commit()

        self._db_mgr.session_lock.release()

    ''' #################################################
        #################################################
    '''
    def _cracking_dictionary_tasks(self):

        self._db_mgr.session_lock.acquire()

        # First we handle the responses

        running_tasks = set()
        self._engine._resp_lock.acquire()
        for channel in list(self._cracking_dictionary_channels.keys()):
            work_id, task_id, count = self._cracking_dictionary_channels[channel]
            if channel in self._engine._responses:
                response = self._engine._responses[channel]
                del(self._engine._responses[channel])
                del(self._cracking_dictionary_channels[channel])
                work = self._db_mgr.session.query(DictionaryTask).\
                                            filter_by(id=work_id).first()

                task = self._db_mgr.session.query(Task).\
                                            filter_by(id=task_id).first()

                if response['status'] == 0:
                    work.state = 'complete'
                    task.done += count
                else:
                    self._db_mgr.session.delete(work)
                    task.state = 'error'
                    if 'error' in response:
                        task.description = response['error']

            else:
                running_tasks.add(task_id)
        self._engine._resp_lock.release()

        self._db_mgr.session.commit()

        #################################################################
        #   Now we check if there're more work to do.
        #################################################################
        
        cracking_tasks = self._db_mgr.session.query(Task).\
            filter_by(stage='cracking.dictionary').\
            filter(Task.protocol == Unit.protocol).\
            filter((Task.state == 'running') | (Task.state == 'ready')).\
            all()

        for task in cracking_tasks:
            # This is only to update the task's state
            if task.id not in running_tasks:
                task.state = 'ready'

            # Update remaining Work (+3 is the offset between plain types and mask types)
            # TODO: filter by task_id too
            weights = [0, 0, 0]
            for row_type in [0, 1, 2]:
                value = self._db_mgr.session.query(func.sum(Dictionary.weight)).\
                                             filter((Dictionary.type == row_type) |\
                                                    (Dictionary.type == row_type + 3)).first()[0]
                
                if value is not None:
                    weights[row_type] = value

            task.total = (weights[0] * weights[1]) + weights[2]

            ###########################################################

            planner = WorkPlanner(self._db_mgr, task, self.work_limit)

            pending_work = planner.get_pending_work()
            if not pending_work:
                continue

            task.state = 'running'
            pending_work['task'] = task.to_json()

            # Load all task's related logs
            logs = []
            parent = task
            while parent:
                logs.extend([json.loads(log) for log in parent.logs])
                parent = parent.parent

            pending_work['logs'] = logs

            response = self._dispatch_task(pending_work)
            # print('[tasker] Dispatch response: {0}'.format(response))

            tracking_info = (planner.work.id, task.id, planner.get_work_weight())
            self._cracking_dictionary_channels[response['channel']] = tracking_info

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

            # waiting.time
            if stage[1] == 'time':
                if int(stage[2]) < (self._db_mgr.timestamp() - task.timestamp)/1000:
                    task.stage = '.'.join(stage[3:])

            # waiting.<log_type>
            # check for log_type (stage[1])
            elif list(filter(lambda log: log['type'] == stage[1], task.parent.logs)):
                task.stage = '.'.join(stage[2:])

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
                                     filter(Task.state != 'error',
                                            Task.state != 'complete',
                                            Task.state != 'stopped').\
                                     all()
        for task in tasks:
            task.state = 'ready'
            if not task.stage.startswith('cracking'):
                task.done = 0
                task.total = 0

        works = self._db_mgr.session.query(DictionaryTask).\
                                     filter(DictionaryTask.state != 'complete').\
                                     all()
        for work in works:
            self._db_mgr.session.delete(work)

        self._db_mgr.session.commit()
        self._db_mgr.session_lock.release()

    ''' #################################################
        #################################################
    '''
    def start(self):

        self.logger.info('Starting Tasker ...')
        self._restart_tasks()

        while not self._engine.halt:
            self.logger.debug('--------------------- new tasker cycle ---------------------')

            # Get units per protocol
            self._units = self._get_protocol_units()

            #self._control_dictionary()

            #self._waiting_tasks()

            self._ready_tasks()
            #self._cracking_dictionary_tasks()

            time.sleep(self._cycle_delay)
