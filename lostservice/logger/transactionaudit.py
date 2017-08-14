#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. currentmodule:: lostservice.logger.auditlog
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

Transaction auditing.
"""
from lostservice.configuration import Configuration
from lostservice.logger.auditlog import AuditableEvent, AuditListener
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine


class TransactionEvent(AuditableEvent):
    """
    Contains all of the fields included in the transaction log.
    """
    def __init__(self):
        """
        Constructor.

        """
        super().__init__()
        self.qpslogid = 1
        self.activityid = 1
        self.serverid = ""  # server id
        self.machineid = ""  # machine id
        self.clientid = ""
        self.starttimeutc = None
        self.endtimeutc = None
        self.transactionms = None
        self.request = ""
        self.response = ""
        self.requesttype = ""  # http request type
        self.requestfindsvctype = ""
        self.requestloctype = ""
        self.requestlocfmt = ""
        self.requestloc = ""
        self.requestlocx = ""
        self.requestlocy = ""
        self.requestlocwkt = ""
        self.requestlocshapetype = ""
        self.requestsvcurn = ""
        self.responsetype = ""
        self.responsesrctype = ""
        self.responsewarningtype = ""
        self.responseerrortype = ""
        self.responselvftype = ""
        self.responsecivgissrctype = ""
        self.notes = ""


Base = declarative_base()


class Transaction(Base):
    """

    """
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


class TransactionAuditListener(AuditListener):
    """
    Implementation for the transaction listener that saves transaction logs to the database.

    """
    def __init__(self, config: Configuration):
        """
        Constructor

        """
        super(TransactionAuditListener, self).__init__()
        self._config = config
        connection_string = self._config.get_logging_db_connection_string()
        engine = create_engine(connection_string)
        Transaction.__table__.create(bind=engine, checkfirst=True)

    def record_event(self, event: TransactionEvent):
        """
        Abstract method for handling auditable events to be implemented by listeners.

         :param event: The event.
         :type event: :py:class:`lostservice.logging.transactionau.AuditableEvent`
        """
        if type(event) is TransactionEvent:
            connection_string = self._config.get_logging_db_connection_string()
            engine = create_engine(connection_string)
            session = sessionmaker()
            session.configure(bind=engine)

            trans = Transaction()
            trans.qpslogid = event.qpslogid  # find the loggin id
            trans.activityid = event.activityid
            trans.serverid = event.serverid  # server id
            trans.machineid = event.machineid  # machine id
            trans.clientid = event.clientid
            trans.starttimeutc = event.starttimeutc
            trans.endtimeutc = event.endtimeutc
            trans.transactionms = event.transactionms
            trans.request = event.request
            trans.response = event.response
            trans.requesttype = event.requesttype  # http request type
            trans.requestfindsvctype = event.requestfindsvctype
            trans.requestloctype = event.requestloctype
            trans.requestlocfmt = event.requestlocfmt
            trans.requestloc = event.requestloc
            trans.requestlocx = event.requestlocx
            trans.requestlocy = event.requestlocy
            trans.requestlocwkt = event.requestlocwkt
            trans.requestlocshapetype = event.requestlocshapetype
            trans.requestsvcurn = event.requestsvcurn
            trans.responsetype = event.responsetype
            trans.responsesrctype = event.responsesrctype
            trans.responsewarningtype = event.responsewarningtype
            trans.responseerrortype = event.responseerrortype
            trans.responselvftype = event.responselvftype
            trans.responsecivgissrctype = event.responsecivgissrctype
            trans.notes = event.notes

            s = session()
            s.add(trans)
            s.commit()
