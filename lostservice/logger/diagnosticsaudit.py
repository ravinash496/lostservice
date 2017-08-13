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


class DiagnosticEvent(AuditableEvent):
    """
    Contains all of the fields included in the transaction log.
    """
    def __init__(self):
        """
        Constructor.

        """
        super().__init__()
        self.qpslogid = ""
        self.eventid = ""
        self.priority = ""
        self.severity = ""
        self.activityid = ""
        self.categoryname = ""
        self.title = ""
        self.timestamputc = ""
        self.machinename = ""
        self.serverid = ""
        self.machineid = ""
        self.message = ""
        self.formattedmessage = ""


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


class DiagnosticAuditListener(AuditListener):
    """
    Implementation for the transaction listener that saves transaction logs to the database.

    """
    def __init__(self, config: Configuration):
        """
        Constructor

        """
        super(DiagnosticAuditListener, self).__init__()
        self._config = config
        connection_string = self._config.get_logging_db_connection_string()
        engine = create_engine(connection_string)
        Diagnostic.__table__.create(bind=engine, checkfirst=True)

    def record_event(self, event: DiagnosticEvent):
        """
        Abstract method for handling auditable events to be implemented by listeners.

         :param event: The event.
         :type event: :py:class:`lostservice.logging.transactionau.AuditableEvent`
        """
        if type(event) is DiagnosticEvent:
            connection_string = self._config.get_logging_db_connection_string()
            engine = create_engine(connection_string)
            session = sessionmaker()
            session.configure(bind=engine)

            diag = Diagnostic()
            diag.qpslogid = event.qpslogid
            diag.eventid = event.eventid
            diag.priority = event.priority
            diag.severity = event.severity
            diag.activityid = event.activityid
            diag.categoryname = event.categoryname
            diag.title = event.title
            diag.timestamputc = event.timestamputc
            diag.machinename = event.machinename
            diag.serverid = event.serverid
            diag.machineid = event.machineid
            diag.message = event.message
            diag.formattedmessage = event.formattedmessage

            s = session()
            s.add(diag)
            s.commit()
