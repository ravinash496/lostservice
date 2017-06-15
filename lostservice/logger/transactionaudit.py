#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. currentmodule:: lostservice.logger.auditlog
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

Transaction auditing.
"""

class TransactionEvent:
    """
    Contains all of the fields included in the transaction log.
    """
    def __init__(self):
        """
        Constructor.

        """
        """
        transactionlogid integer

        qpslogid
        integer,

        activityid
        character

        serverid
        character

        machineid
        character

        clientid
        character

        starttimeutc
        timestamp

        endtimeutc
        timestamp

        transactionms
        integer,

        response
        text

        requesttype
        character

        requestfindsvctype
        character

        requestloctype

        requestlocfmt
        character

        requestloc
        text

        requestlocx
        character

        requestlocy
        character

        requestlocwkt
        character

        requestlocshapetype
        character
        requestsvcurn
        character

        responsetype
        character

        responsesrctype
        character

        responsewarningtype
        character

        responseerrortype
        character

        responselvftype
        character

        responsecivgissrctype
        character

        notes
        text
        """
