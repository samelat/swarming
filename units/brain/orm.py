
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Session = sessionmaker()
ORMBase = declarative_base()

class DBMgr:
    def __init__(self):
        self._engine = create_engine('sqlite:///context.db', echo=True)
        ORMBase.metadata.create_all(self._engine)
        Session.configure(bind=self._engine)
        self._session = Session()

    def add(self, instance):
        self._session.add(instance)
        self._session.flush()
        self._session.refresh(instance)


''' ORM Classes
'''
class SubUnit(ORMBase):

    __tablename__ = 'subunit'
    sunit_id = Column(Integer, primary_key=True)
    command = Column(String)
    protocol = Column(String)
    hostname = Column(String)
    port = Column(Integer)
    path = Column(String)
    context = Column(String)
    timestamp = Column(Integer)

