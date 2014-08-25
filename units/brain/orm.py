
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
        self.session.add(instance)
        self.session.flush()
        self.session.refresh(instance)

    def jsonify(self, row):
        json_row = {}
        values = vars(row)
        for field in row._fields:
            json_row[field] = values[field]
        return json_row


''' ORM Classes
'''
class SubUnit(ORMBase):

    _fields = ['sunit_id', 'command', 'protocol', 'hostname', 'port', 'path', 'context', 'state']
    __tablename__ = 'subunit'
    sunit_id = Column(Integer, primary_key=True)
    command = Column(String)
    protocol = Column(String)
    hostname = Column(String)
    port = Column(Integer)
    path = Column(String)
    context = Column(String)
    state = Column(String)
    timestamp = Column(Integer)

class Instance(ORMBase):
    __tablename__ = 'instance'
    inst_id  = Column(Integer, primary_key=True)
    sunit_id = Column(Integer, ForeignKey('subunit.sunit_id'))

