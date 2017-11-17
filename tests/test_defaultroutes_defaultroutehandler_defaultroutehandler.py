#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from unittest.mock import patch
from unittest.mock import MagicMock
from lostservice.defaultroutes.defaultroutehandler import DefaultSetting, DefaultRouteHandler, OverrideRouteSetting


class DefaultRouteHandlerTest(unittest.TestCase):

    @patch('lostservice.defaultroutes.defaultroutehandler.DefaultRouteConfigWrapper')
    def test__get_default_civic_route(self, mock_config):
        mock_config.settings_for_default_route = MagicMock()
        default_routes: [DefaultSetting]  = [OverrideRouteSetting("OverrideRoute",
                                                                  'urn:nena:service:sos',
                                                                  'sip:sos@oakgrove.ngesi.maine.gov'),
                                             OverrideRouteSetting('OverrideRoute',
                                                                  'urn:nena: service:sos.police',
                                                                  'sip:sos@portlandpd.ngesi.maine.gov')]

        mock_config.settings_for_default_route.return_value = default_routes

        target = DefaultRouteHandler(mock_config)
        actual = target._get_default_civic_route('urn:nena:service:sos')

        self.assertEqual(actual, 'sip:sos@oakgrove.ngesi.maine.gov')

    @patch('lostservice.defaultroutes.defaultroutehandler.DefaultRouteConfigWrapper')
    def test__get_default_civic_route_no_match(self, mock_config):
        mock_config.settings_for_default_route = MagicMock()
        default_routes: [DefaultSetting] = [OverrideRouteSetting("OverrideRoute",
                                                                 'urn:nena:service:sos',
                                                                 'sip:sos@oakgrove.ngesi.maine.gov'),
                                            OverrideRouteSetting('OverrideRoute',
                                                                 'urn:nena: service:sos.police',
                                                                 'sip:sos@portlandpd.ngesi.maine.gov')]
        mock_config.settings_for_default_route.return_value = default_routes

        target = DefaultRouteHandler(mock_config)
        actual = target._get_default_civic_route('urn:nena:service:sos.ambulance')

        self.assertEqual(actual, None)
