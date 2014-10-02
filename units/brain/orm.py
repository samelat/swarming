
import json
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

Session = sessionmaker()
ORMBase = declarative_base()

class ORM:
    def __init__(self):
        self._engine = create_engine('sqlite:///context.db', echo=True)
        ORMBase.metadata.create_all(self._engine)
        Session.configure(bind=self._engine)
        self.session = Session()
        self.classes = [Protocol, BorderUnit, Service, Login,
                        LoginTask, Resource, ResourceTask, Dictionary]
        self.tables = dict([(c.__tablename__, c) for c in self.classes])

    def set(self, table, values):
        try:
            row = self.from_json(tables, values)
            row_id = row.id
            self.session.commit()
        except:
            traceback.print_exc()
            row_id = -1
        #row.timestamp = self.timestamp()
        #self._db_mgr.add(row)
        return row_id

    def from_json(table, values):
        table_class = self.tables[table]
        to_set, conditions = table_class.get_dependencies(values, self)

        if 'id' in values:
            row = session.query(table_class).\
                          filter_by(id=values['id']).\
                          first()
        else:
            row_attrs = dict([(attr, values[attr]) for attr in table_class.attributes
                                                   if  attr in values])
            row = session.query(table_class).\
                          filter_by(**row_attrs).\
                          filter(*conditions).\
                          first()
            if row:
                return row
            to_set.update(row_attrs)
            row = table_class()
            session.add(row)

        for key, value in to_set.items():
            setattr(row, key, value)

        session.flush()

        return row

    def get(self, table):
        pass

    def halt(self):
        self.session.commit()
        self.session.close()


''' ORM Classes
'''
class Protocol(ORMBase):
    __tablename__ = 'protocol'

    attributes = ['name']

    id = Column(Integer, primary_key=True)
    bunit_id = Column(Integer, ForeignKey('border_unit.id'))
    name = Column(String)

    @staticmethod
    def get_dependencies(values, mgr):
        return ({}, [])

    @staticmethod
    def from_json(values, session):
        to_set = Protocol.get_dependencies(values, mgr)        

        if 'id' in values:
            row = session.query(Protocol).\
                          filter_by(id=values['id']).\
                          first()
        else:
            conditions = dict([(attr, values[attr]) for attr in Protocol.attributes if attr in values])
            row = session.query(Protocol).\
                          filter_by(**conditions).\
                          first()
            if row:
                return row
            to_set.update(conditions)
            row = Protocol()
            session.add(row)

        for key, value in to_set.items():
            setattr(row, key, value)

        session.flush()

        return row

class BorderUnit(ORMBase):
    __tablename__ = 'border_unit'

    attributes = ['name']

    id = Column(Integer, primary_key=True)
    name = Column(String)
    timestamp = Column(Integer)
    protocols = relationship('Protocol', backref='bunit')

    @staticmethod
    def get_dependencies(values, mgr):
        to_set = {}
        if 'protocols' in values:
            to_set['protocols'] = [Protocol.from_json(value, session) for value in values['protocols']]
        return (to_set, [])

    @staticmethod
    def from_json(values, session):
        to_set = BorderUnit.get_dependencies(values, session)        

        if 'id' in values:
            row = session.query(BorderUnit).\
                          filter_by(id=values['id']).\
                          first()
        else:
            conditions = dict([(attr, values[attr]) for attr in BorderUnit.attributes if attr in values])
            row = session.query(BorderUnit).\
                          filter_by(**conditions).\
                          first()
            if row:
                return row
            to_set.update(conditions)
            row = BorderUnit()
            session.add(row)

        for key, value in to_set.items():
            setattr(row, key, value)

        session.flush()

        return row

    def to_json(self):
        return {'id':self.id,
                'name':self.name,
                'protocols':[proto.to_json() for proto in self.protocols]}


class Service(ORMBase):
    __tablename__ = 'service'

    attributes = []

    id = Column(Integer, primary_key=True)
    protocol_id = Column(Integer, ForeignKey('protocol.id'))
    hostname = Column(String)
    port = Column(Integer)
    protocol = relationship('Protocol')

    @staticmethod
    def get_dependencies(values, mgr):
        if 'protocol' in values:
            proto = mgr.from_json('protocol', values['protocol'])
        return ({'protocol':proto}, [Service.protocol_id==proto.id])

    @staticmethod
    def from_json(values, session):
        print('[Service]')
        if 'protocol' in values:
            protocol = Protocol.from_json(values['protocol'], session)

        if 'id' in values:
            row = session.query(Service).\
                          filter_by(id=values['id']).\
                          first()
        else:            
            row = session.query(Service).\
                          filter_by(hostname=values['hostname'],
                                    port=values['port'],
                                    protocol_id=protocol.id).\
                          first()
            if row:
                return row
            row = Service()
            row.protocol = protocol
            session.add(row)

        if 'hostname' in values:
            row.hostname = values['hostname']
        
        if 'port' in values:
            row.port = values['port']

        session.flush()

        return row

    def to_json(self):
        return {'id':self.id,
                'protocol':self.protocol.to_json(),
                'hostname':self.hostname,
                'port':self.port}


class Login(ORMBase):
    __tablename__ = 'login'
    
    attributes = []
    depending  = []

    id = Column(Integer, primary_key=True)
    service_id = Column(Integer, ForeignKey('service.id'))
    dependence_id = Column(Integer, ForeignKey('login.id'))
    path = Column(String)
    params = Column(String)
    attrs = Column(String)
    timestamp = Column(Integer)
    service = relationship('Service', backref='logins')
    dependence = relationship('Login')

    @staticmethod
    def from_json(values, session):
        print('[Login]')
        if 'service' in values:
            service = Service.from_json(values['service'], session)

        if 'id' in values:
            row = session.query(Login).\
                          filter_by(id=values['id']).\
                          first()
        else:            
            row = session.query(Login).\
                          filter_by(path=values['path'],
                                    service_id=service.id).\
                          first()
            if row:
                return row
            row = Login()
            row.service = service
            session.add(row)

        if 'path' in values:
            row.path = values['path']
        
        if 'attrs' in values:
            row.attrs = json.dumps(values['attrs'])

        if 'params' in values:
            row.params = json.dumps(values['params'])

        session.flush()

        return row

    def to_json(self):
        return {'id':self.id,
                'path':self.path,
                'params':json.loads(self.params),
                'attrs':json.loads(self.attrs),
                'service':self.service.to_json()}


class Dictionary(ORMBase):
    __tablename__ = 'dictionary'

    attributes = []
    depending  = []

    id = Column(Integer, primary_key=True)
    timestamp = Column(Integer)

class LoginTask(ORMBase):
    __tablename__ = 'login_task'

    attributes = []
    depending  = []

    id = Column(Integer, primary_key=True)
    login_id = Column(Integer, ForeignKey('login.id'))
    bunit_id = Column(String,  ForeignKey('border_unit.id'))
    dict_id = Column(Integer, ForeignKey('dictionary.id'))
    state = Column(String)
    command = Column(String)
    timestamp = Column(Integer)

class Resource(ORMBase):
    __tablename__ = 'resource'

    attributes = []
    depending  = []

    id = Column(Integer, primary_key=True)
    service_id = Column(Integer, ForeignKey('service.id'))
    dependence_id = Column(Integer, ForeignKey('login.id'))
    path = Column(String)
    params = Column(String)
    attrs = Column(String)
    timestamp = Column(Integer)
    service = relationship('Service', backref='resources')
    dependence = relationship('Login')

class ResourceTask(ORMBase):
    __tablename__ = 'resource_task'

    attributes = []
    depending  = []

    id = Column(Integer, primary_key=True)
    resource_id = Column(Integer, ForeignKey('resource.id'))
    bunit_id = Column(String, ForeignKey('border_unit.id'))
    state = Column(String)
    command = Column(String)
    timestamp = Column(Integer)



