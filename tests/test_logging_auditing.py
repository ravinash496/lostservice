#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from unittest.mock import patch
from unittest.mock import MagicMock
import lostservice.logging.auditlog as auditlog


class AuditLogTest(unittest.TestCase):

    def test_audit_noop(self):
        target = auditlog.AuditLog()
        try:
            target.record_event(None)
        except:
            self.fail("record_event threw an exception.")

    @patch('test_logging_auditing.auditlog.AuditListener')
    def test_audit_none(self, mocklistener):
        target = auditlog.AuditLog()
        mocklistener.record_event = MagicMock()
        target.register_listener(mocklistener)

        target.record_event(None)

        mocklistener.record_event.assert_called_once()
        mocklistener.record_event.assert_called_with(None)

    @patch('test_logging_auditing.auditlog.AuditListener')
    def test_audit_simple(self, mocklistener):
        target = auditlog.AuditLog()
        mocklistener.record_event = MagicMock()
        target.register_listener(mocklistener)
        event = auditlog.AuditableEvent()

        target.record_event(event)

        mocklistener.record_event.assert_called_once()
        mocklistener.record_event.assert_called_with(event)
