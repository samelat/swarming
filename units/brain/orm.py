
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Session = sessionmaker()
ORMBase = declarative_base()

class DBMgr:
    def __init__(self):
        self._engine = create_engine('sqlite:///context.db', echo=True)
        ORMBase.metadata.create_all(self._engine)
        Session.configure(bind=self._engine)
        self.session = Session()

    def add(self, instance):
        print('[DBMgr] Estamos agregando una subunit: {0}'.format(instance))
        self.session.add(instance)
        self.session.flush()
        self.session.refresh(instance)

    def jsonify(self, row):
        json_row = {}
        values = vars(row)
        for field in row._fields:
            json_row[field] = values[field]
        return json_row

    def halt(self):
        self.session.commit()
        self.session.close()


''' ORM Classes
'''
class Unit(ORMBase):
    __tablename__ = 'unit'
    unit_id = Column(Integer, primary_key=True)
    task = Column(Integer)
    state = Column(String)
    timestamp = Column(Integer)

class Activity(ORMBase):
    __tablename__ = 'activity'
    activity_id = Column(Integer, primary_key=True)
    unit_id = Column(Integer, ForeignKey('unit.unit_id'))
    resource_id = Column(Integer, ForeignKey('resource.resource_id'))
    command = Column(String)
    method = Column(String)

class Resource(ORMBase):
    _fields = ['resource_id', 'protocol', 'hostname', 'port', 'path']
    __tablename__ = 'resource'
    resource_id = Column(Integer, primary_key=True)
    method = Column(String)
    protocol = Column(String)
    hostname = Column(String)
    port = Column(Integer)
    path = Column(String)
    params = Column(String)
    attrs = Column(String)
    timestamp = Column(Integer)

'''
class Instance(ORMBase):
    __tablename__ = 'instance'
    inst_id  = Column(Integer, primary_key=True)
    sunit_id = Column(Integer, ForeignKey('subunit.sunit_id'))
'''

