#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from unittest.mock import patch
from unittest.mock import MagicMock
import lostservice.handling.core
import lostservice.handling.findservice
import lostservice.model.requests
import lostservice.model.responses

import lostservice.model.location


class FindServiceTest(unittest.TestCase):

    @patch('lostservice.handling.findservice.FindServiceOuter')
    @patch('lostservice.coverage.resolver.CoverageResolverWrapper')
    def test_handle_point(self, mock_outer, mock_cov):

        # Mock for apply_policy_settings.
        mock_outer.find_service_for_point = MagicMock()

        expected = lostservice.model.responses.FindServiceResponse()
        mock_outer.find_service_for_point.return_value = expected

        mock_cov.check_coverage = MagicMock()
        mock_cov.check_coverage.return_value = 'some.server.name'

        target = lostservice.handling.core.FindServiceHandler(mock_outer, mock_cov)

        model = lostservice.model.requests.FindServiceRequest()
        model.location = lostservice.model.location.Location()
        model.location.location = lostservice.model.geodetic.Point()

        try:
            actual = target.handle_request(model, {})
            mock_outer.find_service_for_point.assert_called_once()
            mock_outer.find_service_for_point.assert_called_with(model)
            self.assertTrue(actual is expected, 'Response did not match expected value.')

        except:
            self.fail("handle_request threw an exception.")

    @patch('lostservice.handling.findservice.FindServiceOuter')
    @patch('lostservice.coverage.resolver.CoverageResolverWrapper')
    def test_handle_circle(self, mock_outer, mock_cov):

        # Mock for apply_policy_settings.
        mock_outer.find_service_for_circle = MagicMock()
        expected = lostservice.model.responses.FindServiceResponse()
        mock_outer.find_service_for_circle.return_value = expected

        mock_cov.check_coverage = MagicMock()
        mock_cov.check_coverage.return_value = 'some.server.name'

        target = lostservice.handling.core.FindServiceHandler(mock_outer, mock_cov)

        model = lostservice.model.requests.FindServiceRequest()
        model.location = lostservice.model.location.Location()
        model.location.location = lostservice.model.geodetic.Circle()

        try:
            actual = target.handle_request(model, {})
            mock_outer.find_service_for_circle.assert_called_once()
            mock_outer.find_service_for_circle.assert_called_with(model)
            self.assertTrue(actual is expected, 'Response did not match expected value.')

        except:
            self.fail("handle_request threw an exception.")

    @patch('lostservice.handling.findservice.FindServiceOuter')
    @patch('lostservice.coverage.resolver.CoverageResolverWrapper')
    def test_handle_ellipse(self, mock_outer, mock_cov):

        # Mock for apply_policy_settings.
        mock_outer.find_service_for_ellipse = MagicMock()
        expected = lostservice.model.responses.FindServiceResponse()
        mock_outer.find_service_for_ellipse.return_value = expected

        mock_cov.check_coverage = MagicMock()
        mock_cov.check_coverage.return_value = 'some.server.name'

        target = lostservice.handling.core.FindServiceHandler(mock_outer, mock_cov)

        model = lostservice.model.requests.FindServiceRequest()
        model.location = lostservice.model.location.Location()
        model.location.location = lostservice.model.geodetic.Ellipse()

        try:
            actual = target.handle_request(model, {})
            mock_outer.find_service_for_ellipse.assert_called_once()
            mock_outer.find_service_for_ellipse.assert_called_with(model)
            self.assertTrue(actual is expected, 'Response did not match expected value.')

        except:
            self.fail("handle_request threw an exception.")

    @patch('lostservice.handling.findservice.FindServiceOuter')
    @patch('lostservice.coverage.resolver.CoverageResolverWrapper')
    def test_handle_arcband(self, mock_outer, mock_cov):

        # Mock for apply_policy_settings.
        mock_outer.find_service_for_arcband = MagicMock()
        expected = lostservice.model.responses.FindServiceResponse()
        mock_outer.find_service_for_arcband.return_value = expected

        mock_cov.check_coverage = MagicMock()
        mock_cov.check_coverage.return_value = 'some.server.name'

        target = lostservice.handling.core.FindServiceHandler(mock_outer, mock_cov)

        model = lostservice.model.requests.FindServiceRequest()
        model.location = lostservice.model.location.Location()
        model.location.location = lostservice.model.geodetic.Arcband()

        try:
            actual = target.handle_request(model, {})
            mock_outer.find_service_for_arcband.assert_called_once()
            mock_outer.find_service_for_arcband.assert_called_with(model)
            self.assertTrue(actual is expected, 'Response did not match expected value.')

        except:
            self.fail("handle_request threw an exception.")

    @patch('lostservice.handling.findservice.FindServiceOuter')
    @patch('lostservice.coverage.resolver.CoverageResolverWrapper')
    def test_handle_polygon(self, mock_outer, mock_cov):

        # Mock for apply_policy_settings.
        mock_outer.find_service_for_polygon = MagicMock()
        expected = lostservice.model.responses.FindServiceResponse()
        mock_outer.find_service_for_polygon.return_value = expected

        mock_cov.check_coverage = MagicMock()
        mock_cov.check_coverage.return_value = 'some.server.name'

        target = lostservice.handling.core.FindServiceHandler(mock_outer, mock_cov)

        model = lostservice.model.requests.FindServiceRequest()
        model.location = lostservice.model.location.Location()
        model.location.location = lostservice.model.geodetic.Polygon()

        try:
            actual = target.handle_request(model, {})
            mock_outer.find_service_for_polygon.assert_called_once()
            mock_outer.find_service_for_polygon.assert_called_with(model)
            self.assertTrue(actual is expected, 'Response did not match expected value.')

        except:
            self.fail("handle_request threw an exception.")

    @patch('lostservice.handling.findservice.FindServiceOuter')
    @patch('lostservice.coverage.resolver.CoverageResolverWrapper')
    def test_handle_failure(self, mock_outer, mock_cov):

        # Mock for apply_policy_settings.
        mock_outer.find_service_for_polygon = MagicMock()

        mock_cov.check_coverage = MagicMock()
        mock_cov.check_coverage.return_value = 'some.server.name'

        target = lostservice.handling.core.FindServiceHandler(mock_outer, mock_cov)

        model = lostservice.model.requests.FindServiceRequest()
        model.location = lostservice.model.location.Location()
        model.location.location = None

        with self.assertRaises(lostservice.exception.BadRequestException):
            target.handle_request(model, {})


if __name__ == '__main__':
    unittest.main()
