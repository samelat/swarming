
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
        self._engine = create_engine('sqlite:///context.db', echo=True)
        ORMBase.metadata.create_all(self._engine)
        Session.configure(bind=self._engine)
        self.session = Session()
        self.session_lock = lock

        self.classes = [Protocol, Unit, Service, Resource, Task, Dictionary]
        self.tables = dict([(c.__tablename__, c) for c in self.classes])

    def timestamp(self):
        return int(time.time() * 1000)

    def set(self, table, values):
        try:
            row = self.from_json(table, values)
            row_id = row.id
            print('[orm.set] id={0}'.format(row_id))
            self.session.commit()
        except:
            traceback.print_exc()
            row_id = -1
        #row.timestamp = self.timestamp()
        #self._db_mgr.add(row)
        return row_id

    def from_json(self, table, values):
        table_class = self.tables[table]
        to_set, conditions = table_class.get_dependencies(values, self)

        if 'id' in values:
            row = self.session.query(table_class).\
                               filter_by(id=values['id']).\
                               first()
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

        for key, value in to_set.items():
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
class Protocol(ORMBase):
    __tablename__ = 'protocol'

    attributes = ['name']

    id = Column(Integer, primary_key=True)
    unit_id = Column(Integer, ForeignKey('unit.id'))
    name = Column(String)
    timestamp = Column(Integer)

    @staticmethod
    def get_dependencies(values, mgr):
        return ({}, [])

    def to_json(self):
        return {'id':self.id,
                'name':self.name}

''' ################################################
'''
class Unit(ORMBase):
    __tablename__ = 'unit'

    attributes = ['name']

    id = Column(Integer, primary_key=True)
    name = Column(String)
    timestamp = Column(Integer)
    
    protocols = relationship('Protocol', backref='unit')

    @staticmethod
    def get_dependencies(values, mgr):
        to_set = {}
        if 'protocols' in values:
            to_set['protocols'] = [mgr.from_json('protocol', protocol) for protocol in values['protocols']]
        return (to_set, [])

    def to_json(self):
        return {'id':self.id,
                'name':self.name,
                'protocols':[protocol.to_json() for protocol in self.protocols]}

''' ################################################
'''
class Service(ORMBase):
    __tablename__ = 'service'

    attributes = ['hostname', 'port']

    id = Column(Integer, primary_key=True)
    protocol_id = Column(Integer, ForeignKey('protocol.id'))
    hostname = Column(String)
    port = Column(Integer)
    timestamp = Column(Integer)

    protocol = relationship('Protocol')

    @staticmethod
    def get_dependencies(values, mgr):
        if 'protocol' in values:
            proto = mgr.from_json('protocol', values['protocol'])
        return ({'protocol':proto}, [Service.protocol_id==proto.id])

    def to_json(self):
        return {'id':self.id,
                'protocol':self.protocol.to_json(),
                'hostname':self.hostname,
                'port':self.port}


''' ################################################
'''
class Resource(ORMBase):
    __tablename__ = 'resource'

    attributes = ['path']

    id = Column(Integer, primary_key=True)
    service_id = Column(Integer, ForeignKey('service.id'))
    dependence_id = Column(Integer, ForeignKey('resource.id'))
    path = Column(String, default='')
    params = Column(String, default='{}')
    attrs = Column(String, default='{}')
    timestamp = Column(Integer, default=0)

    service = relationship('Service')
    dependence = relationship('Resource')

    @staticmethod
    def get_dependencies(values, mgr):
        to_set = {}
        conditions = []

        for key in ['params', 'attrs']:
            if key in values:
                to_set[key] = json.dumps(values[key])

        for key, table in [('service', 'service'), ('dependence', 'resource')]:
            if key in values:
                to_set[key] = mgr.from_json(table, values[key])

        if 'service' in to_set:
            conditions.append(Resource.service_id==to_set['service'].id)

        return (to_set, conditions)

    def to_json(self):
        return {'id':self.id,
                'path':self.path,
                'params':json.loads(self.params),
                'attrs':json.loads(self.attrs),
                'service':self.service.to_json()}

''' ################################################
'''
class Dictionary(ORMBase):
    __tablename__ = 'dictionary'

    attributes = []

    id = Column(Integer, primary_key=True)
    timestamp = Column(Integer)

    @staticmethod
    def get_dependencies(values, mgr):
        to_set = {}
        if 'protocols' in values:
            to_set['protocols'] = [mgr.from_json('protocol', value) for value in values['protocols']]
        return (to_set, [])


''' ################################################
'''
class Task(ORMBase):
    __tablename__ = 'task'

    attributes = ['stage']

    id = Column(Integer, primary_key=True)
    resource_id = Column(Integer, ForeignKey('resource.id'))
    stage = Column(String, default='initial')
    state = Column(String, default='stopped')
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
