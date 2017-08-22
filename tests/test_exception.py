#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import lostservice.exception as exp

message_format = '<{0} message="{1}" xml:lang="en"/>'
error_format = \
    """<?xml version="1.0" encoding="UTF-8"?><errors xmlns="urn:ietf:params:xml:ns:lost1" source="{0}">{1}</errors>"""


class ExceptionTest(unittest.TestCase):

    def test_bad_request(self):
        actual = str(exp.BadRequestException('bad request', None))
        expected = message_format.format('badRequest', 'bad request')
        self.assertEqual(actual, expected)

    def test_forbidden(self):
        actual = str(exp.ForbiddenException('forbidden', None))
        expected = message_format.format('forbidden', 'forbidden')
        self.assertEqual(actual, expected)

    def test_internal_error(self):
        actual = str(exp.InternalErrorException('internal error', None))
        expected = message_format.format('internalError', 'internal error')
        self.assertEqual(actual, expected)

    def test_build_error_response(self):
        inner_expected = message_format.format('badRequest', 'bad request')
        expected = error_format.format('some.uri', inner_expected)
        actual = exp.build_error_response(exp.BadRequestException('bad request', None), 'some.uri')
        self.assertEqual(actual, expected)

    def test_build_error_response_not_lost(self):
        inner_expected = message_format.format('internalError', 'some random exception')
        expected = error_format.format('some.uri', inner_expected)
        actual = exp.build_error_response(Exception('some random exception'), 'some.uri')
        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
