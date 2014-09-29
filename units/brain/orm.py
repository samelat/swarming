
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
        self.table_classes = {BorderUnit.__tablename__:BorderUnit}

    def get_table_classes(self):
        table_classes = {}
        for _class in ORMBase._decl_class_registry.values():
            if hasattr(_class, '__tablename__'):
                table_classes[_class.__tablename__] = _class
        return table_classes

    def add(self, row):
        print('[DBMgr] Estamos agregando una fila: {0}'.format(row))
        self.session.add(row)
        self.session.commit()
        self.session.flush()
        self.session.refresh(row)

    def halt(self):
        self.session.commit()
        self.session.close()


''' ORM Classes
'''
class Protocol(ORMBase):
    __tablename__ = 'protocol'
    id = Column(Integer, primary_key=True)
    bunit_id = Column(Integer, ForeignKey('border_unit.id'))
    name = Column(String)

    @staticmethod
    def from_json(values, session):



class BorderUnit(ORMBase):
    __tablename__ = 'border_unit'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    timestamp = Column(Integer)
    protocols = relationship('Protocol')

    @staticmethod
    def from_json(values, session):
        rows = session.query(BorderUnit).filter_by(name=values['name']).all()
        if not rows:
            row = BorderUnit(name=values['name'])
            for protocol in values['protocols']:
                row.protocols.append(Protocol.from_json(protocol))
            rows = [row]
        return rows[0]

    def to_json(self):
        return {'name':self.name,
                'protocols':[proto.name for proto in self.protocols]}


class Service(ORMBase):
    __tablename__ = 'service'
    id = Column(Integer, primary_key=True)
    proto_id = Column(Integer, ForeignKey('protocol.id'))
    hostname = Column(String)
    port = Column(Integer)
    protocol = relationship('Protocol')

    @staticmethod
    def from_json(values, session):
        rows = session.query(Service).filter_by(name=values['protocol'],
                                                hostname=values['hostname'],
                                                ).all()
        if not rows:
            row = Service(values['hostname'], values['port'])
            row.protocol = Protocol.from_json(values['protocol'])

        return 

    def to_json(self):
        return {'id':self.id,
                'protocol':self.protocol.name,
                'hostname':self.hostname,
                'port':self.port}


class Login(ORMBase):
    __tablename__ = 'login'
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
        self.path = values['path']
        self.params = json.dumps(values['params'])
        self.attrs = json.dumps(values['attrs'])
        service = values['service']
        if 'id' in service:
            self.service = session.query(Service).\
                                   filter_by(id=service['id']).one()
        else:
            self.service = Service()
            self.service.from_json(values['service'], session)

    def to_json(self):
        return {'path':self.path,
                'params':json.loads(self.params),
                'attrs':json.loads(self.attrs),
                'service':self.service.to_json()}

class Dictionary(ORMBase):
    __tablename__ = 'dictionary'
    id = Column(Integer, primary_key=True)
    timestamp = Column(Integer)

class LoginTask(ORMBase):
    __tablename__ = 'login_task'
    id = Column(Integer, primary_key=True)
    login_id = Column(Integer, ForeignKey('login.id'))
    bunit_id = Column(String,  ForeignKey('border_unit.id'))
    dict_id = Column(Integer, ForeignKey('dictionary.id'))
    state = Column(String)
    command = Column(String)
    timestamp = Column(Integer)

class Resource(ORMBase):
    __tablename__ = 'resource'
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
    id = Column(Integer, primary_key=True)
    resource_id = Column(Integer, ForeignKey('resource.id'))
    bunit_id = Column(String, ForeignKey('border_unit.id'))
    state = Column(String)
    command = Column(String)
    timestamp = Column(Integer)



