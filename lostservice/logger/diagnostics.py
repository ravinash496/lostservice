#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. currentmodule:: lostservice.logger.auditlog
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

Transaction auditing.
"""
from lostservice.model.diagnostic import Diagnostic
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class DiagnosticsEvent:
    """
    Contains all of the fields included in the diagnostics log.
    """
    def __init__(self):
        """
        Constructor.
        """
        qpslogid = ""
        eventid = ""
        priority = ""
        severity = ""
        activityid = ""
        categoryname = ""
        title = ""
        timestamputc = ""
        machinename = ""
        serverid = ""
        machineid = ""
        message = ""
        formattedmessage = ""

    def log(self):
        connection_string = self.conf.get_db_connection_string(section="Logging")
        engine = create_engine(connection_string)
        session = sessionmaker()
        session.configure(bind=engine)

        diag = Diagnostic()
        diag.qpslogid = self.qpslogid
        diag.eventid = self.eventid
        diag.priority = self.priority
        diag.severity = self.severity
        diag.activityid = self.activityid
        diag.categoryname = self.categoryname
        diag.title = self.title
        diag.timestamputc = self.timestamputc
        diag.machinename = self.machinename
        diag.serverid = self.serverid
        diag.machineid = self.machineid
        diag.message = self.message
        diag.formattedmessage = self.formattedmessage

        s = session()
        s.add(diag)
        s.commit()
        return True