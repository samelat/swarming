
import time
import json
import traceback
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

Session = sessionmaker()
ORMBase = declarative_base()


class ORM:
    def __init__(self, lock):
        self._engine = create_engine('sqlite:///context.db', echo=False)
        ORMBase.metadata.create_all(self._engine)
        Session.configure(bind=self._engine)
        self.session = Session()
        self.session_lock = lock

        self.classes = [Unit, Resource, Task, Dictionary, Success]
        self.tables = dict([(c.__tablename__, c) for c in self.classes])


    def timestamp(self):
        return int(time.time() * 1000)


    def set(self, table, values):
        cls = self.tables[table]
        error, row = cls.from_json(values, self)
        self.session.commit()

        if error < 0:
            return error
        return row.to_json(simple=True)


    def get(self, table, values):
        cls = self.tables[table]

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
                return (-2, None)

            for attr in cls.attributes:
                if attr in values:
                    to_set[attr] = values[attr]
        else:
            row_attrs = dict([(attr, values[attr]) for attr in cls.attributes
                                                   if  attr in values])
            
            conditions = cls.get_conditions(to_set)
            row = mgr.session.query(cls).\
                               filter_by(**row_attrs).\
                               filter(*conditions).\
                               first()
            if row:
                return (0, row)
            to_set.update(row_attrs)
            row = cls()
            mgr.session.add(row)

        for key, value in to_set.items():
            setattr(row, key, value)

        row.timestamp = mgr.timestamp()

        mgr.session.flush()

        return (0, row)

    @staticmethod
    def get_conditions(to_set):
        return []

    @staticmethod
    def get_to_set(values, mgr):
        return (0, {})


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

    def to_json(self, simple=False):
        if simple:
            return {'id':self.id}
        return {'id':self.id,
                'name':self.name,
                'protocols':[protocol.to_json() for protocol in self.protocols]}


''' ################################################
    ################################################
'''
class Resource(ORMBase, ORMCommon):
    __tablename__ = 'resource'

    attributes = ['protocol', 'hostname', 'port', 'path']

    id = Column(Integer, primary_key=True)
    dependence_id = Column(Integer, ForeignKey('resource.id'))

    protocol = Column(String)
    hostname = Column(String)
    port = Column(Integer)
    path = Column(String, default='/')
    attrs = Column(String, default='{}')
    complete = Column(Boolean, default=False) # DO NOT confuse with complete task stage.

    timestamp = Column(Integer, default=0)

    @staticmethod
    def get_conditions(to_set):
        conditions = []

        if 'attrs' in to_set:
            conditions.append(Resource.attrs==to_set['attrs'])

        if 'dependence_id' in to_set:
            conditions.append(Resource.dependence_id==to_set['dependence_id'])

        return conditions

    @staticmethod
    def get_to_set(values, mgr):
        to_set = {}

        if 'attrs' in values:
            to_set['attrs'] = json.dumps(values['attrs'])

        if 'dependence' in values:
            error, row = Resource.from_json(values['dependence'], mgr)
            if error < 0:
                return (error, None)
            to_set['dependence_id'] = row.id

        return (0, to_set)


    def to_json(self, simple=False):
        if simple:
            return {'id':self.id}
        values = {'id':self.id,
                  'protocol':self.protocol,
                  'hostname':self.hostname,
                  'port':self.port,
                  'path':self.path,
                  'attrs':json.loads(self.attrs),
                  'timestamp':self.timestamp}
        if self.dependence_id:
            values['dependence'] = {'id':self.dependence_id}
        return values


''' ################################################
    ################################################
'''
class Task(ORMBase, ORMCommon):
    __tablename__ = 'task'

    attributes = ['stage', 'state']

    id = Column(Integer, primary_key=True)
    resource_id = Column(Integer, ForeignKey('resource.id'))
    stage = Column(String, default='initial') # (initial, crawling, forcing, waiting, complete)
    state = Column(String, default='ready') # (ready, stopped, running)
    timestamp = Column(Integer)

    resource = relationship('Resource')

    @staticmethod
    def get_to_set(values, mgr):
        to_set = {}
        if 'resource' in values:
            error, row = Resource.from_json(values['resource'], mgr)
            if error < 0:
                return (error, None)
            to_set['resource'] = row

        return (0, to_set)

    def to_json(self, simple=False):
        if simple:
            return {'id':self.id, 'resource':self.resource.to_json(True)}
        return {'id':self.id,
                'stage':self.stage,
                'state':self.state,
                'resource':self.resource.to_json()}


''' ################################################
    ################################################
'''
class Dictionary(ORMBase, ORMCommon):
    __tablename__ = 'dictionary'

    attributes = ['username', 'password']

    id = Column(Integer, primary_key=True)
    resource_id = Column(Integer, ForeignKey('resource.id'))

    username = Column(String)
    password = Column(String)
    timestamp = Column(Integer)

    def to_json(self, simple=False):
        if simple:
            return {'id':self.id}
        values = {'id':self.id,
                  'username':self.username,
                  'password':self.password}
        if self.resource_id:
            values['resource'] = {'id':self.resource_id}


''' ################################################
    ################################################
'''
class Success(ORMBase, ORMCommon):
    __tablename__ = 'success'

    attributes = ['username', 'password']

    id = Column(Integer, primary_key=True)
    resource_id = Column(Integer, ForeignKey('resource.id'))

    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    timestamp = Column(Integer)

    def to_json(self, simple=False):
        return {'id':self.id,
                'username':self.username,
                'password':self.password,
                'resource':{'id':self.resource_id}}


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

