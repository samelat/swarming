
import time
import json
import traceback
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, ForeignKey
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

        self.classes = [Unit, Resource, Task, Dictionary]
        self.tables = dict([(c.__tablename__, c) for c in self.classes])

    def timestamp(self):
        return int(time.time() * 1000)

    def set(self, table, values):
        try:
            row = self.from_json(table, values)
            row_id = row.id
            #print('[orm.set] id={0}'.format(row_id))
            self.session.commit()
        except:
            print('[!] ERROR!!!')
            traceback.print_exc()
            row_id = -1
        #row.timestamp = self.timestamp()
        #self._db_mgr.add(row)
        return row_id

    def from_json(self, table, values):
        table_class = self.tables[table]
        to_set, conditions = table_class.get_dependencies(values, self)

        #print('[orm.from_json] values: {0}'.format(values))
        if 'id' in values:
            row = self.session.query(table_class).\
                               filter_by(id=values['id']).\
                               first()
            for attr in table_class.attributes:
                if attr in values:
                    to_set[attr] = values[attr]
        else:
            row_attrs = dict([(attr, values[attr]) for attr in table_class.attributes
                                                   if  attr in values])
            row = self.session.query(table_class).\
                               filter_by(**row_attrs).\
                               filter(*conditions).\
                               first()
            if row:
                return row
            to_set.update(row_attrs)
            row = table_class()
            self.session.add(row)

        #print('[orm.set] to_set: {0}'.format(to_set))
        for key, value in to_set.items():
            #print('[orm.set] {0} = {1}'.format(key, value))
            setattr(row, key, value)

        row.timestamp = self.timestamp()

        self.session.flush()

        return row

    def get(self, table, timestamp):
        table_class = self.tables[table]

        json_rows = []
        for row in self.session.query(table_class).\
                                filter(table_class.timestamp > timestamp).\
                                all():
            json_rows.append(row.to_json())

        return {'timestamp':self.timestamp(), 'rows':json_rows}

    def halt(self):
        self.session.commit()
        self.session.close()


''' ORM Classes
'''

''' ################################################
'''
class Unit(ORMBase):
    __tablename__ = 'unit'

    attributes = ['name', 'protocol']

    id = Column(Integer, primary_key=True)
    name = Column(String)
    protocol = Column(String)
    timestamp = Column(Integer)

    @staticmethod
    def get_dependencies(values, mgr):
        return ({}, [])

    def to_json(self):
        return {'id':self.id,
                'name':self.name,
                'protocols':[protocol.to_json() for protocol in self.protocols]}


''' ################################################
'''
class Resource(ORMBase):
    __tablename__ = 'resource'

    attributes = ['protocol', 'hostname', 'port', 'path']

    id = Column(Integer, primary_key=True)
    dependence_id = Column(Integer, ForeignKey('resource.id'))

    protocol = Column(String)
    hostname = Column(String)
    port = Column(Integer)
    path = Column(String, default='')
    attrs = Column(String, default='{}')

    timestamp = Column(Integer, default=0)

    dependence = relationship('Resource')

    @staticmethod
    def get_dependencies(values, mgr):
        to_set = {}
        conditions = []

        if 'attrs' in values:
            to_set['attrs'] = json.dumps(values['attrs'])
            conditions.append(Resource.attrs==json.dumps(values['attrs']))

        if 'dependence' in values:
            to_set['dependence'] = mgr.from_json('resource', values['dependence'])

        return (to_set, conditions)

    def to_json(self):
        return {'id':self.id,
                'protocol':self.protocol,
                'hostname':self.hostname,
                'port':self.port,
                'path':self.path,
                'attrs':json.loads(self.attrs)}

''' ################################################

    ################################################
'''
class Dictionary(ORMBase):
    __tablename__ = 'dictionary'

    attributes = ['username', 'password']

    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)
    timestamp = Column(Integer)

    @staticmethod
    def get_dependencies(values, mgr):
        to_set = {}
        if 'protocols' in values:
            to_set['protocols'] = [mgr.from_json('protocol', value) for value in values['protocols']]
        return (to_set, [])

    def to_json(self):
        return {'id':self.id,
                'username':self.username,
                'password':self.password}


''' ################################################
'''
class Task(ORMBase):
    __tablename__ = 'task'

    attributes = ['stage', 'state']

    id = Column(Integer, primary_key=True)
    resource_id = Column(Integer, ForeignKey('resource.id'))
    stage = Column(String, default='initial') # (initial, crawling, forcing, waiting, complete)
    state = Column(String, default='ready') # (ready, stopped, running)
    complete = Column(Integer, default=0)
    timestamp = Column(Integer)

    resource = relationship('Resource')

    @staticmethod
    def get_dependencies(values, mgr):
        to_set = {}
        conditions = []

        if 'resource' in values:
                to_set['resource'] = mgr.from_json('resource', values['resource'])
                conditions.append(Task.resource_id==to_set['resource'].id)

        return (to_set, conditions)

    def to_json(self):
        return {'id':self.id,
                'stage':self.stage,
                'state':self.state,
                'resource':self.resource.to_json()}


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
