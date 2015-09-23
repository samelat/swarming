
import time
import json
import traceback
from threading import Lock

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import UniqueConstraint
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, SmallInteger
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

Session = sessionmaker()
ORMBase = declarative_base()


class ORM:

    _singleton_session = None
    _singleton_session_lock = None

    def __init__(self):
        self._engine = create_engine('sqlite:///context.db', echo=False,
                                     connect_args={'check_same_thread': False})
        '''
        self._engine = create_engine('sqlite://', echo=False,
                                     connect_args={'check_same_thread':False})
        '''
        ORMBase.metadata.create_all(self._engine)
        Session.configure(bind=self._engine)

        if ORM._singleton_session is None:
            ORM._singleton_session = Session()

        if ORM._singleton_session_lock is None:
            ORM._singleton_session_lock = Lock()

        self.session = ORM._singleton_session
        self.session_lock = ORM._singleton_session_lock

        self.classes = [Unit, Task, Dictionary, Success, Register, Log]
        self.entities = dict([(c.__tablename__, c) for c in self.classes])

    @classmethod
    def timestamp(cls):
        return int(time.time() * 1000)

    def post(self, entity, entries):
        print(entries)
        try:
            self._engine.execute(self.entities[entity].__table__.insert(), entries)

        except sqlalchemy.exc.IntegrityError:
            size = len(entries)
            if size > 1:
                increment = int(size/4) if size > 7 else 1
                size += 1 if not size % increment else increment

                begin = 0
                for end in range(increment, size, increment):
                    print('begin: {0} - end: {1}'.format(begin, end))
                    self.post(entity, entries[begin:end])
                    begin = end

        return {'status': 0}

    def put(self, entity, entries):
        cls = self.entities[entity]

        error, values = cls.from_json(entries, self)
        # self.session.commit()

        return {'status': error, 'values': values}

    def get(self, entity, conditions):
        cls = self.entities[entity]

        query = self.session.query(cls)

        if 'id' in conditions:
            query = query.filter(cls.id == conditions['id'])
        elif 'timestamp' in conditions:
            query = query.filter(cls.timestamp > conditions['timestamp'])

        return [row.to_json() for row in query.all()]

    def delete(self, entity, entries):
        cls = self.entities[entity]

        for entry in entries:
            obj = self.session.query(cls).filter(cls.id == entry['id']).first()
            obj.delete()

    def halt(self):
        self.session.commit()
        self.session.close()


################################################
#                 ORM Classes
#                 Common Class
################################################
class ORMCommon:

    attributes = []

    @classmethod
    def from_json(cls, values, mgr):

        error, to_set = cls.get_to_set(values, mgr)
        if error < 0:
            return (error, None)

        # print('[orm.from_json] values: {0}'.format(values))
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
        return [getattr(cls, attr) == to_set[attr] for attr in to_set.keys()]

    @classmethod
    def get_to_set(cls, values, mgr):
        to_set = dict([(attr, value) for attr, value in values.items()
                                     if attr in cls.attributes])
        return (0, to_set)

    @classmethod
    def suit(cls, values):
        result = {'timestamp': ORM.timestamp()}
        
        for field in cls.attributes:
            if field in values:
                result[field] = values[field]
            elif getattr(cls, field).default.arg is not None:
                result[field] = getattr(cls, field).default.arg
            else:
                return None

        return result


#################################################
#
#################################################
class Unit(ORMBase, ORMCommon):
    __tablename__ = 'unit'
    __table_args__ = (UniqueConstraint('name', 'protocol'),)

    attributes = ['name', 'protocol', 'port']

    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False)
    port = Column(Integer, nullable=False)
    protocol = Column(String(32), nullable=False)
    timestamp = Column(Integer)

    def to_json(self):
        return {'id': self.id,
                'name': self.name,
                'port': self.port,
                'protocol': self.protocol}


#################################################
#
#################################################
class Task(ORMBase, ORMCommon):
    __tablename__ = 'task'
    __table_args__ = (UniqueConstraint('protocol', 'hostname', 'port', 'path', 'stage'),)

    attributes = ['protocol', 'hostname', 'port', 'path',
                  'stage', 'state', 'done', 'total', 'description']

    id = Column(Integer, primary_key=True)
    # parent_id = Column(Integer, ForeignKey('task.id'), nullable=True)

    # Task
    stage = Column(String(64), nullable=False, default='initial')  # (initial, crawling, cracking, waiting)
    state = Column(String(64), nullable=False, default='ready')  # (ready, stopped, running, complete, error)
    description = Column(String(128), nullable=False, default='')
    timestamp = Column(Integer, default=0)

    # Resource
    protocol = Column(String(32), nullable=False)
    hostname = Column(String(128), nullable=False)
    port = Column(Integer)
    path = Column(String(128), nullable=False, default='/')
    #attrs = Column(String(1024), nullable=False, default='{}')

    # Work
    done = Column(Integer, default=0)
    total = Column(Integer, default=0)

    logs = relationship('Log', uselist=True)
    # parent = relationship('Task', remote_side=[id])
    registers = relationship('Register', uselist=True)

    @classmethod
    def get_conditions(cls, to_set):
        return [getattr(cls, attr) == to_set[attr]
                for attr in to_set.keys()
                if attr not in ['state', 'stage',
                                'done',  'total',
                                'description']]

    @classmethod
    def get_to_set(cls, values, mgr):

        _, to_set = super(Task, cls).get_to_set(values, mgr)

        #if 'attrs' in values:
        #    to_set['attrs'] = json.dumps(values['attrs'])

        #if 'dependence' in values:
        #    error, row = Task.from_json(values['dependence'], mgr)
        #    if error < 0:
        #        return (error, None)
        #    to_set['dependence_id'] = row['id']

        return (0, to_set)

    def to_json(self):
        values = {'id': self.id,
                  'protocol': self.protocol,
                  'hostname': self.hostname,
                  'port': self.port,
                  'path': self.path,
                  # 'attrs': json.loads(self.attrs),
                  'stage': self.stage,
                  'state': self.state,
                  'done': self.done,
                  'total': self.total,
                  'description': self.description,
                  'timestamp': self.timestamp}

        #if self.dependence_id:
        #    values['dependence'] = {'id': self.dependence.id}

        #if self.complement:
        #    values['complement'] = self.complement.to_json()

        return values


#################################################
#
#################################################
class Success(ORMBase, ORMCommon):
    __tablename__ = 'success'

    attributes = []

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('task.id'))

    # The string lenght should be greater for other types of credencials
    credentials = Column(String(512), nullable=False)
    timestamp = Column(Integer)

    task = relationship('Task', uselist=False)

    @classmethod
    def get_to_set(cls, values, mgr):
        to_set = {}
        to_set['task_id'] = values['task']['id']
        to_set['credentials'] = json.dumps(values['credentials'])
        return (0, to_set)

    # The attribute Stage in the JSON response is precent to help
    # in the identification of what kind of credentials the entry have.
    def to_json(self):
        return {'id': self.id,
                'credentials': json.loads(self.credentials),
                'task': {'id': self.task_id, 'stage': self.task.stage}}


#################################################
#
#################################################
class Register(ORMBase, ORMCommon):
    __tablename__ = 'register'

    attributes = []

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('task.id'))

    type = Column(String(64), nullable=False)
    content = Column(String(1024), nullable=False)
    timestamp = Column(Integer)

    @classmethod
    def get_to_set(cls, values, mgr):
        to_set = {}
        if 'task' in values:
            to_set['task_id'] = values['task']['id']
        to_set['values'] = json.dumps(values['values'])
        return (0, to_set)

    def to_json(self):
        return {'id': self.id,
                'type': self.type,
                'content': json.loads(self.values),
                'task': {'id': self.task_id}}


#################################################
#
#################################################
class Log(ORMBase, ORMCommon):
    __tablename__ = 'log'

    attributes = []

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('task.id'))

    type = Column(String(64), nullable=False)
    content = Column(String(1024), nullable=False)
    timestamp = Column(Integer)

    @classmethod
    def get_to_set(cls, values, mgr):
        to_set = {}
        if 'task' in values:
            to_set['task_id'] = values['task']['id']
        to_set['values'] = json.dumps(values['values'])
        return (0, to_set)

    def to_json(self):
        return {'id': self.id,
                'type': self.type,
                'content': json.loads(self.values),
                'task': {'id': self.task_id}}


#################################################
#   Dictionary Types
#   0: plain username
#   1: plain password
#   2: plain pair
#   3: mask username
#   4: mask password
#   5: mask pair
#################################################
class Dictionary(ORMBase, ORMCommon):
    __tablename__ = 'dictionary'
    __table_args__ = (UniqueConstraint('type', 'username', 'password', 'charsets'),)

    attributes = ['type', 'username', 'password']

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('task.id'))

    type = Column(SmallInteger, nullable=False, default=-1)
    username = Column(String(32), nullable=False, default='')
    password = Column(String(32), nullable=False, default='')
    charsets = Column(String(256), nullable=False, default='{}')
    weight   = Column(Integer, nullable=False, default=1)
    timestamp = Column(Integer)

    @classmethod
    def get_to_set(cls, values, mgr):
        _, to_set = super(cls, cls).get_to_set(values, mgr)
        if 'type' in values:
            to_set['type'] = values['type']
        elif 'username' in values:
            if 'password' in values:
                to_set['type'] = 2 # Pair
            else:
                to_set['type'] = 0 # Username
        else:
            to_set['type'] = 1 # Password

        if 'charsets' in values:
            to_set['charsets'] = json.dumps(values['charsets'])

        if 'task' in values:
            to_set['task_id'] = values['task']['id']
        return (0, to_set)

    @classmethod
    def suit(cls, values):
        result = super(cls, cls).suit(values)
        # print('[result] {0}'.format(result))
        if result and (result['type'] < 0):
            if result['username']:
                if result['password']:
                    result['type'] = 2 # Pair
                else:
                    result['type'] = 0 # Username
            else:
                result['type'] = 1 # Password
        return result

    def to_json(self):
        values = {'id':self.id, 'weight':self.weight, 'type':self.type}
        if self.type in [0, 3]:
            values['username'] = self.username
        elif self.type in [1, 4]:
            values['password'] = self.password
        else:
            values['username'] = self.username
            values['password'] = self.password

        if self.charsets != '{}':
            values['charsets'] = json.loads(self.charsets)

        if self.task_id:
            values['task'] = {'id':self.task_id}
        return values


#################################################
# These classes are for internal use only
#################################################
class DictionaryTask(ORMBase):
    __tablename__ = 'dictionary_task'

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('task.id'))

    index = Column(Integer)
    current = Column(Integer)
    # channel = Column(Integer)
    state = Column(String(64), default='running') # (running, complete)
    timestamp = Column(Integer)

    task = relationship('Task')
