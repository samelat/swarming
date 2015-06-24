
import time
import json
import traceback
from threading import Lock

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
                                     connect_args={'check_same_thread':False})
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

        self.classes = [Unit, Task, Dictionary, Success, Complement]
        self.entities = dict([(c.__tablename__, c) for c in self.classes])

    @classmethod
    def timestamp(cls):
        return int(time.time() * 1000)

    '''
    def check(self, entity, fields):
        if entity not in self.entities:
            return False

        if not set(fields).issubset(self.entities[entity].attributes):
            return False

        return True
    '''

    def add(self, entity, values):
        #for chunk in [values[i:i+400] for i in range(0, len(values), 400)]:
        try:
            self._engine.execute(self.entities[entity].__table__.insert(), values)
        except sqlalchemy.exc.IntegrityError:
            print('[rollback]')
            self.session.rollback()
            for value in values:
                self.set(entity, value)
            self.session.commit()

        return {'status':0}


    def set(self, entity, values):
        cls = self.entities[entity]
        error, values = cls.from_json(values, self)
        #self.session.commit()

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

    @classmethod
    def suit(cls, values):
        result = {}
        if 'timestamp' not in values:
            result['timestamp'] = ORM.timestamp()
        for field, value in values.items():
            if value and field in cls.attributes:
                result[field] = value
        return result


''' ################################################
    ################################################
'''
class Unit(ORMBase, ORMCommon):
    __tablename__ = 'unit'

    attributes = ['name', 'protocol', 'port']

    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False)
    port = Column(Integer, nullable=False)
    protocol = Column(String(32), nullable=False)
    timestamp = Column(Integer)

    def to_json(self):
        return {'id':self.id,
                'name':self.name,
                'port':self.port,
                'protocol':self.protocol}


''' ################################################
    ################################################
'''
class Task(ORMBase, ORMCommon):
    __tablename__ = 'task'
    __table_args__ = (UniqueConstraint('protocol', 'hostname', 'port', 'path',
                                       'stage', 'attr'),)

    attributes = ['protocol', 'hostname', 'port', 'path',
                  'stage',    'state',    'done', 'total',
                  'description']

    id = Column(Integer, primary_key=True)
    dependence_id = Column(Integer, ForeignKey('task.id'))

    # Task
    stage = Column(String(64), nullable=False, default='initial') # (initial, crawling, cracking, waiting)
    state = Column(String(64), nullable=False, default='ready') # (ready, stopped, running, complete, error)
    description = Column(String(128), nullable=False, default='')
    timestamp = Column(Integer, default=0)

    # Resource
    protocol = Column(String(32), nullable=False)
    hostname = Column(String(128), nullable=False)
    port = Column(Integer)
    path = Column(String(128), nullable=False, default='/')
    attrs = Column(String(1024), nullable=False, default='{}')

    # Work
    done = Column(Integer, default=0)
    total = Column(Integer, default=0)

    dependence = relationship('Task', remote_side=[id])
    complement = relationship('Complement', uselist=False)

    @classmethod
    def get_conditions(cls, to_set):
        return [getattr(cls, attr)==to_set[attr] for attr in to_set.keys()
                                                 if  attr not in ['state', 'stage',
                                                                  'done',  'total',
                                                                  'description']]

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
                  'done':self.done,
                  'total':self.total,
                  'description':self.description,
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
        return {'id':self.id,
                'credentials':json.loads(self.credentials),
                'task':{'id':self.task_id, 'stage':self.task.stage}}


''' ################################################
    ################################################
'''
class Complement(ORMBase, ORMCommon):
    __tablename__ = 'complement'

    attributes = []

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('task.id'))

    values = Column(String(1024), nullable=False)
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
    Dictionary
    0: username - 1: password - 2: pairs
    ################################################
'''

class Dictionary(ORMBase, ORMCommon):
    __tablename__ = 'dictionary'
    __table_args__ = (UniqueConstraint('type', 'username', 'password', 'charsets'),)

    attributes = ['type', 'username', 'password']

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('task.id'))

    type = Column(SmallInteger, nullable=False, default=2)
    username = Column(String(32), nullable=False, default='')
    password = Column(String(32), nullable=False, default='')
    charsets = Column(String(256), nullable=False, default='{}')
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
        if 'type' not in result:
            if 'username' in values:
                if 'password' in values:
                    result['type'] = 2 # Pair
                else:
                    result['type'] = 0 # Username
            else:
                result['type'] = 1 # Password
        return result

    def to_json(self):
        values = {'id':self.id}
        if self.type == 0:
            values['username'] = self.username
        elif self.type == 1:
            values['password'] = self.password
        else:
            values['username'] = self.username
            values['password'] = self.password

        if self.charsets != '{}':
            values['charsets'] = json.loads(self.charsets)

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
    # channel = Column(Integer)
    state = Column(String(64), default='running') # (running, complete)
    timestamp = Column(Integer)

    task = relationship('Task')
