#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from unittest.mock import patch
from unittest.mock import MagicMock
import lostservice


class AuditLogTest(unittest.TestCase):

    def test_audit_noop(self):
        target = lostservice.logger.auditlog.AuditLog()
        try:
            target.record_event(None)
        except:
            self.fail("record_event threw an exception.")

    @patch('lostservice.logger.auditlog.AuditListener')
    def test_audit_none(self, mocklistener):
        target = lostservice.logger.auditlog.AuditLog()
        mocklistener.record_event = MagicMock()
        target.register_listener(mocklistener)

        target.record_event(None)

        mocklistener.record_event.assert_called_once()
        mocklistener.record_event.assert_called_with(None)

    @patch('lostservice.logger.auditlog.AuditListener')
    def test_audit_simple(self, mocklistener):
        target = lostservice.logger.auditlog.AuditLog()
        mocklistener.record_event = MagicMock()
        target.register_listener(mocklistener)
        event = lostservice.logger.auditlog.AuditableEvent()

        target.record_event(event)

        mocklistener.record_event.assert_called_once()
        mocklistener.record_event.assert_called_with(event)


if __name__ == '__main__':
    unittest.main()
