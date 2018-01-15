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
from geoalchemy2 import Geometry
from geoalchemy2 import shape
from shapely.geometry import Point

class TransactionEvent(AuditableEvent):
    """
    Contains all of the fields included in the transaction log.
    """
    def __init__(self):
        """
        Constructor.

        """
        super().__init__()
        self.qps_log_id = 1
        self.activity_id = 1
        self.server_id = ""  # server id
        self.machine_id = ""  # machine id
        self.client_id = ""
        self.start_time_utc = None
        self.end_time_utc = None
        self.transaction_ms = None
        self.request = ""
        self.response = ""
        self.request_type = ""  # http request type
        self.request_find_svc_type = ""
        self.request_loc_type = ""
        self.request_loc_fmt = ""
        self.request_loc = ""
        self.request_loc_x = ""
        self.request_loc_y = ""
        self.request_loc_wkt = ""
        self.request_loc_shape_type = ""
        self.request_svc_urn = ""
        self.response_type = ""
        self.response_src_type = ""
        self.response_warning_type = ""
        self.response_error_type = ""
        self.response_lvf_type = ""
        self.response_civ_gis_src_type = ""
        self.notes = ""
        self.wkb_geometry = None


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
    wkb_geometry = Column(Geometry(geometry_type='Point', srid=4326))


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
            trans.qpslogid = event.qps_log_id  # find the logging id
            trans.activityid = event.activity_id
            trans.serverid = event.server_id  # server id
            trans.machineid = event.machine_id  # machine id
            trans.clientid = event.client_id
            trans.starttimeutc = event.start_time_utc
            trans.endtimeutc = event.end_time_utc
            trans.transactionms = event.transaction_ms
            trans.request = event.request
            trans.response = event.response
            trans.requesttype = event.request_type  # http request type
            trans.requestfindsvctype = event.request_find_svc_type
            trans.requestloctype = event.request_loc_type
            trans.requestlocfmt = event.request_loc_fmt
            trans.requestloc = event.request_loc
            trans.requestlocx = event.request_loc_x
            trans.requestlocy = event.request_loc_y
            trans.requestlocwkt = event.request_loc_wkt
            trans.requestlocshapetype = event.request_loc_shape_type
            trans.requestsvcurn = event.request_svc_urn
            trans.responsetype = event.response_type
            trans.responsesrctype = event.response_src_type
            trans.responsewarningtype = event.response_warning_type
            trans.responseerrortype = event.response_error_type
            trans.responselvftype = event.response_lvf_type
            trans.responsecivgissrctype = event.response_civ_gis_src_type
            trans.notes = event.notes

            location_point = Point(event.request_loc_x, event.request_loc_y)
            trans.wkb_geometry = shape.from_shape(location_point, srid=4326)

            s = session()
            s.add(trans)
            s.commit()
