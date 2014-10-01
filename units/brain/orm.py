
import json
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

Session = sessionmaker()
ORMBase = declarative_base()

class DBMgr:
    def __init__(self):
        self._engine = create_engine('sqlite:///context.db', echo=True)
        ORMBase.metadata.create_all(self._engine)
        Session.configure(bind=self._engine)
        self.session = Session()
        self.classes = [Protocol, BorderUnit, Service, Login,
                        LoginTask, Resource, ResourceTask, Dictionary]
        self.tables = dict([(c.__tablename__, c) for c in self.classes])

    def halt(self):
        self.session.commit()
        self.session.close()

    def row_from_json(self, table, values):
        # First, we resolve the dependences
        attributes = {}
        depending = {}

        table_class = self.tables['table']

        for key in tables_class.depending:
            if key in values:
                depending[key] = Protocol.from_json(values['protocol'], session)

        if 'id' in values:
            row = session.query(tables_class).\
                          filter_by(id=values['id']).\
                          first()
        else:            
            query = session.query(tables_class).\
                          filter_by(name=values['name']).\
                          first()
            if row:
                return row
            row = Protocol()
            session.add(row)

        if 'name' in values:
            row.name = values['name']

        session.flush()

        return row


''' ORM Classes
'''
class Protocol(ORMBase):
    __tablename__ = 'protocol'

    attributes = ['name']
    depending  = ['border_unit']

    id = Column(Integer, primary_key=True)
    bunit_id = Column(Integer, ForeignKey('border_unit.id'))
    name = Column(String)

    @staticmethod
    def from_json(values, session):
        print('[Protocol]')
        if 'id' in values:
            row = session.query(Protocol).\
                          filter_by(id=values['id']).\
                          first()
        else:            
            row = session.query(Protocol).\
                          filter_by(name=values['name']).\
                          first()
            if row:
                return row
            row = Protocol()
            session.add(row)

        if 'name' in values:
            row.name = values['name']

        session.flush()

        return row

class BorderUnit(ORMBase):
    __tablename__ = 'border_unit'

    attributes = []
    depending  = []

    id = Column(Integer, primary_key=True)
    name = Column(String)
    timestamp = Column(Integer)
    protocols = relationship('Protocol', backref='bunit')

    @staticmethod
    def from_json(values, session):
        rows = session.query(BorderUnit).filter_by(name=values['name']).all()
        if not rows:
            row = BorderUnit(name=values['name'])
            for protocol in values['protocols']:
                row.protocols.append(Protocol.from_json(protocol, session))
            return row
        
        return rows[0]

    def to_json(self):
        return {'id':self.id,
                'name':self.name,
                'protocols':[proto.to_json() for proto in self.protocols]}


class Service(ORMBase):
    __tablename__ = 'service'

    attributes = []
    depending  = []

    id = Column(Integer, primary_key=True)
    protocol_id = Column(Integer, ForeignKey('protocol.id'))
    hostname = Column(String)
    port = Column(Integer)
    protocol = relationship('Protocol')

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



