#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. currentmodule:: lostservice.logger.auditlog
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

Transaction auditing.
"""
from lostservice.model.transaction import Transaction
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class TransactionEvent:
    """
    Contains all of the fields included in the transaction log.
    """
    def __init__(self):
        """
        Constructor.
        """
        self.conf = None
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

    def log(self):
        connection_string = self.conf.get_db_connection_string(section="Logging")
        engine = create_engine(connection_string)
        session = sessionmaker()
        session.configure(bind=engine)

        trans = Transaction()
        trans.qpslogid = self.qpslogid # find the loggin id
        trans.activityid = self.activityid
        trans.serverid = self.serverid  # server id
        trans.machineid = self.machineid  # machine id
        trans.clientid = self.clientid
        trans.starttimeutc = self.starttimeutc
        trans.endtimeutc = self.endtimeutc
        trans.transactionms = self.transactionms
        trans.request = self.request
        trans.response = self.response
        trans.requesttype = self.requesttype  # http request type
        trans.requestfindsvctype = self.requestfindsvctype
        trans.requestloctype = self.requestloctype
        trans.requestlocfmt = self.requestlocfmt
        trans.requestloc = self.requestloc
        trans.requestlocx = self.requestlocx
        trans.requestlocy = self.requestlocy
        trans.requestlocwkt = self.requestlocwkt
        trans.requestlocshapetype = self.requestlocshapetype
        trans.requestsvcurn = self.requestsvcurn
        trans.responsetype = self.responsetype
        trans.responsesrctype = self.responsesrctype
        trans.responsewarningtype = self.responsewarningtype
        trans.responseerrortype = self.responseerrortype
        trans.responselvftype = self.responselvftype
        trans.responsecivgissrctype = self.responsecivgissrctype
        trans.notes = self.notes

        s = session()
        s.add(trans)
        s.commit()
        return True