from sqlalchemy.sql import func
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime,Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Transaction(Base):
    __tablename__ = 'transactionlog'
    transactionlogid = Column(Integer, primary_key=True)
    qpslogid = Column(Integer)
    activityid = Column(String(64))
    serverid = Column(String(64))
    machineid = Column(String(64))
    clientid = Column(String(128))
    starttimeutc = Column(DateTime, default=func.now())
    endtimeutc = Column(DateTime, default=func.now())
    transactionms = Column(Integer)
    request = Column(Text)
    response = Column(Text)
    requesttype = Column(String(48))
    requestfindsvctype = Column(String(48))
    requestloctype = Column(String(48))
    requestlocfmt = Column(String(48))
    requestloc = Column(Text)
    requestlocx = Column(String(32))
    requestlocy = Column(String(32))
    requestlocwkt = Column(Text)
    requestlocshapetype = Column(String(32))
    requestsvcurn = Column(String(48))
    responsetype = Column(String(48))
    responsesrctype = Column(String(48))
    responsewarningtype = Column(String(48))
    responseerrortype = Column(String(48))
    responselvftype = Column(String(48))
    responsecivgissrctype = Column(String(48))
    notes = Column(Text)