from sqlalchemy.sql import func
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime,Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Diagnostic(Base):
    __tablename__ = 'diagnosticlog'
    logid = Column(Integer, primary_key=True)
    qpslogid = Column(Integer)
    eventid = Column(Integer)
    priority = Column(Integer)
    severity = Column(String(32))
    activityid = Column(String(64))
    categoryname = Column(String(64))
    title = Column(String(256))
    timestamputc = Column(DateTime, default=func.now())
    machinename = Column(String(32))
    serverid = Column(String(64))
    machineid = Column(String(64))
    message = Column(Text)
    formattedmessage = Column(Text)