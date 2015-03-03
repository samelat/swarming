
import time
import json
import traceback
from threading import Lock

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

Session = sessionmaker()
ORMBase = declarative_base()


class ORM:

    _singleton_session_lock = None

    def __init__(self):

        if ORM._singleton_session_lock is None:
            ORM._singleton_session_lock = Lock()

        self._engine = create_engine('sqlite:///context.db', echo=False,
                                     connect_args={'check_same_thread':False})
        ORMBase.metadata.create_all(self._engine)
        Session.configure(bind=self._engine)
        self.session = Session()
        self.session_lock = ORM._singleton_session_lock

        self.classes = [Unit, Task, Dictionary, Success, Complement]
        self.entities = dict([(c.__tablename__, c) for c in self.classes])


    def timestamp(self):
        return int(time.time() * 1000)


    def set(self, entity, values):
        cls = self.entities[entity]
        error, values = cls.from_json(values, self)
        self.session.commit()

        return {'status':error, 'values':values}


    def get(self, entity, values):
        cls = self.entities[entity]

        timestamp = 0
        if 'timestamp' in values:
            timestamp = values['timestamp']

        json_rows = []

        if 'id' in values:
            condition = (cls.id==values['id'])
        else:
            condition = (cls.timestamp > timestamp)

        for row in self.session.query(cls).\
                                filter(condition).\
                                all():
            json_rows.append(row.to_json())

        return {'rows':json_rows}


    def halt(self):
        self.session.commit()
        self.session.close()


''' ################################################
                    ORM Classes
                    Common Class
    ################################################
'''
class ORMCommon:

    @classmethod
    def from_json(cls, values, mgr):

        error, to_set = cls.get_to_set(values, mgr)
        if error < 0:
            return (error, None)

        #print('[orm.from_json] values: {0}'.format(values))
        if 'id' in values:
            row = mgr.session.query(cls).\
                               filter_by(id=values['id']).\
                               first()

            if ('timestamp' in values) and (values['timestamp'] < row.timestamp):
                # You have to refresh your reference.
                return (-2, row.to_json())
        else:
            
            conditions = cls.get_conditions(to_set)
            row = mgr.session.query(cls).\
                               filter(*conditions).\
                               first()
            if row:
                return (1, {'id':row.id})

            row = cls()
            mgr.session.add(row)

        for key, value in to_set.items():
            setattr(row, key, value)

        row.timestamp = mgr.timestamp()

        mgr.session.flush()

        return (0, {'id':row.id})

    @classmethod
    def get_conditions(cls, to_set):
        return [getattr(cls, attr)==to_set[attr] for attr in to_set.keys()]

    @classmethod
    def get_to_set(cls, values, mgr):
        to_set = dict([(attr, value) for attr, value in values.items()
                                     if  attr in cls.attributes])
        return (0, to_set)


''' ################################################
    ################################################
'''
class Unit(ORMBase, ORMCommon):
    __tablename__ = 'unit'

    attributes = ['name', 'protocol']

    id = Column(Integer, primary_key=True)
    name = Column(String)
    protocol = Column(String)
    timestamp = Column(Integer)

    def to_json(self):
        return {'id':self.id,
                'name':self.name,
                'protocol':self.protocol}


''' ################################################
    ################################################
'''
class Task(ORMBase, ORMCommon):
    __tablename__ = 'task'

    attributes = ['protocol', 'hostname', 'port', 'path', 'stage', 'state']

    id = Column(Integer, primary_key=True)
    dependence_id = Column(Integer, ForeignKey('task.id'))

    # Task
    stage = Column(String, default='initial') # (initial, crawling, forcing, waiting, complete)
    state = Column(String, default='ready') # (ready, stopped, running)
    timestamp = Column(Integer, default=0)

    # Resource
    protocol = Column(String)
    hostname = Column(String)
    port = Column(Integer)
    path = Column(String, default='/')
    attrs = Column(String, default='{}')

    dependence = relationship('Task', remote_side=[id])
    complement = relationship('Complement', uselist=False)

    @classmethod
    def get_conditions(cls, to_set):
        return [getattr(cls, attr)==to_set[attr] for attr in to_set.keys()
                                                 if  attr not in ['state', 'stage']]

    @classmethod
    def get_to_set(cls, values, mgr):

        _, to_set = super(Task, cls).get_to_set(values, mgr)

        if 'attrs' in values:
            to_set['attrs'] = json.dumps(values['attrs'])

        if 'dependence' in values:
            error, row = Task.from_json(values['dependence'], mgr)
            if error < 0:
                return (error, None)
            to_set['dependence_id'] = row['id']

        return (0, to_set)

    def to_json(self):
        values = {'id':self.id,
                  'protocol':self.protocol,
                  'hostname':self.hostname,
                  'port':self.port,
                  'path':self.path,
                  'attrs':json.loads(self.attrs),
                  'stage':self.stage,
                  'state':self.state,
                  'timestamp':self.timestamp}
        if self.dependence_id:
            values['dependence'] = {'id':self.dependence.id}

        if self.complement:
            values['complement'] = self.complement.to_json()

        return values


''' ################################################
    ################################################
'''
class Success(ORMBase, ORMCommon):
    __tablename__ = 'success'

    attributes = []

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('task.id'))

    credentials = Column(String, nullable=False)
    timestamp = Column(Integer)

    @classmethod
    def get_to_set(cls, values, mgr):
        to_set = {}
        to_set['task_id'] = values['task']['id']
        to_set['credentials'] = json.dumps(values['credentials'])
        return (0, to_set)

    def to_json(self):
        return {'id':self.id,
                'credentials':json.loads(self.credentials),
                'task':{'id':self.task_id}}


''' ################################################
    ################################################
'''
class Complement(ORMBase, ORMCommon):
    __tablename__ = 'complement'

    attributes = []

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('task.id'))

    values = Column(String, nullable=False)
    timestamp = Column(Integer)

    @classmethod
    def get_to_set(cls, values, mgr):
        to_set = {}
        if 'task' in values:
            to_set['task_id'] = values['task']['id']
        to_set['values'] = json.dumps(values['values'])
        return (0, to_set)

    def to_json(self):
        return {'id':self.id,
                'values':json.loads(self.values)}


''' ################################################
    ################################################
'''
class Dictionary(ORMBase, ORMCommon):
    __tablename__ = 'dictionary'

    attributes = ['username', 'password']

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('task.id'))

    username = Column(String)
    password = Column(String)
    timestamp = Column(Integer)

    @classmethod
    def get_to_set(cls, values, mgr):
        _, to_set = super(Dictionary, cls).get_to_set(values, mgr)
        if 'task' in values:
            to_set['task_id'] = values['task']['id']
        return (0, to_set)

    def to_json(self):
        values = {'id':self.id,
                  'username':self.username,
                  'password':self.password}
        if self.task_id:
            values['task'] = {'id':self.task_id}
        return values


''' ################################################
    These classes are for internal use only
    ################################################
'''
class DictionaryTask(ORMBase):
    __tablename__ = 'dictionary_task'

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('task.id'))

    index = Column(Integer)
    current = Column(Integer)
    channel = Column(Integer)
    state = Column(String, default='stopped') # (stopped, running, complete)
    timestamp = Column(Integer)

    task = relationship('Task')
