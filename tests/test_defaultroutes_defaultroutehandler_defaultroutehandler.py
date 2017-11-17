#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from unittest.mock import patch
from unittest.mock import MagicMock
from lostservice.defaultroutes.defaultroutehandler import DefaultSetting, DefaultRouteHandler, OverrideRouteSetting
from lostservice.defaultroutes.defaultroutehandler import ExistingRouteSetting


class DefaultRouteHandlerTest(unittest.TestCase):

    @patch('lostservice.defaultroutes.defaultroutehandler.DefaultRouteConfigWrapper')
    def test__get_default_civic_route_override(self, mock_config):
        mock_config.settings_for_default_route = MagicMock()
        default_routes: [DefaultSetting] = [OverrideRouteSetting('OverrideRoute',
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

    @patch('lostservice.defaultroutes.defaultroutehandler.DefaultRouteConfigWrapper')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test__get_default_civic_route_existing(self, mock_config, mock_db):
        mock_config.settings_for_default_route = MagicMock()
        default_routes: [DefaultSetting] = [OverrideRouteSetting('OverrideRoute',
                                                                 'urn:nena:service:sos',
                                                                 'sip:sos@oakgrove.ngesi.maine.gov'),
                                            ExistingRouteSetting('ExistingRoute',
                                                                 'urn:nena:service:sos.police',
                                                                 '{AFF10CC6-54F2-4A43-AE12-D8881CD550A4}',
                                                                 mock_db)]

        mock_config.settings_for_default_route.return_value = default_routes
        mock_db.get_urn_table_mappings = MagicMock()
        mock_db.get_urn_table_mappings.return_value = {'urn:nena:service:sos.police': 'esblaw'}
        mock_db.get_boundaries_for_previous_id = MagicMock()
        mock_db.get_boundaries_for_previous_id.return_value = [{'routeuri': 'sip:sos@portlandpd.ngesi.maine.gov'}]

        target = DefaultRouteHandler(mock_config)
        actual = target._get_default_civic_route('urn:nena:service:sos.police')

        self.assertEqual(actual, 'sip:sos@portlandpd.ngesi.maine.gov')
