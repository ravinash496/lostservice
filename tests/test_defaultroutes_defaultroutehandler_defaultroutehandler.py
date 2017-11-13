#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from unittest.mock import patch
from unittest.mock import MagicMock
import lostservice.defaultroutes.defaultroutehandler


class DefaultRouteHandlerTest(unittest.TestCase):

    @patch('lostservice.defaultroutes.defaultroutehandler.DefaultRouteConfigWrapper')
    def test__get_default_civic_route(self, mock_config):
        mock_config.settings_for_default_route = MagicMock()
        mock_config.settings_for_default_route.return_value = {'default_routes': [
            {'mode': 'OverrideRoute', 'urn': 'urn:nena:service:sos', 'uri': 'sip:sos@oakgrove.ngesi.maine.gov'},
            {'mode': 'OverrideRoute', 'urn': 'urn:nena:service:sos.police',
             'uri': 'sip:sos@portlandpd.ngesi.maine.gov'}]}

        target = lostservice.defaultroutes.defaultroutehandler.DefaultRouteHandler(mock_config)
        actual = target._get_default_civic_route('urn:nena:service:sos')

        self.assertEqual(actual, 'sip:sos@oakgrove.ngesi.maine.gov')

    @patch('lostservice.defaultroutes.defaultroutehandler.DefaultRouteConfigWrapper')
    def test__get_default_civic_route_no_match(self, mock_config):
        mock_config.settings_for_default_route = MagicMock()
        mock_config.settings_for_default_route.return_value = {'default_routes': [
            {'mode': 'OverrideRoute', 'urn': 'urn:nena:service:sos', 'uri': 'sip:sos@oakgrove.ngesi.maine.gov'},
            {'mode': 'OverrideRoute', 'urn': 'urn:nena:service:sos.police',
             'uri': 'sip:sos@portlandpd.ngesi.maine.gov'}]}

        target = lostservice.defaultroutes.defaultroutehandler.DefaultRouteHandler(mock_config)
        actual = target._get_default_civic_route('urn:nena:service:sos.ambulance')

        self.assertEqual(actual, None)
