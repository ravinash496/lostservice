#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. currentmodule:: lostservice.logger.auditlog
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

Auditing framework.
"""

import logging


class AuditableEvent(object):
    """
    Encapsulates all of the information that can be part of an audit event.

    """
    def __init__(self):
        """
        Constructor.
        """
        super(AuditableEvent, self).__init__()


class AuditListener(object):
    """
    Base class for classes that are destinations for auditing.

    """
    def __init__(self):
        """
        Constructor

        """
        super(AuditListener, self).__init__()

    def record_event(self, event):
        """
        Abstract method for handling auditable events to be implemented by listeners.

         :param event: The event.
         :type event: :py:class:`lostservice.logging.auditlog.AuditableEvent`
        """
        raise NotImplementedError('The record_event method must be implemented in a subclass.')


class AuditLog(object):
    """
    Class for handling audit logger.

    """
    def __init__(self):
        """
        Constructor.
        """
        super(AuditLog, self).__init__()
        self._listeners = []
        self._logger = logging.getLogger('lostservice.logger.auditlog.AuditLog')

    def record_event(self, event):
        """
        Records the given event with all registered listeners.

        :param event: The event to record.
        :type event: :py:class:`lostservice.logging.auditlog.AuditableEvent`
        """
        self._logger.info('recording event')
        self._logger.debug(event)
        for listener in self._listeners:
            listener.record_event(event)

    def register_listener(self, listener):
        """
        Registers the given listener.

        :param listener: The listener to register.
        :type listener: :py:class:`lostservice.logging.auditlog.AuditListener`
        """
        self._logger.info('registering listener')
        self._logger.debug('listener')
        self._listeners.append(listener)



