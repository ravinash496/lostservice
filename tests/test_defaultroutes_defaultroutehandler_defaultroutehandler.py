#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from unittest.mock import patch
from unittest.mock import MagicMock
from lostservice.defaultroutes.defaultroutehandler import DefaultSetting, \
    DefaultRouteHandler, OverrideRouteSetting, CivicMatchingSetting, DefaultRouteModeEnum
from lostservice.defaultroutes.defaultroutehandler import ExistingRouteSetting
from lostservice.model.requests import FindServiceRequest
from lostservice.model.location import Location
from lostservice.model.civic import CivicAddress


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
        request = FindServiceRequest(service='urn:nena:service:sos')
        actual = target._get_default_civic_route(request)

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
        request = FindServiceRequest(service='urn:nena:service:sos.ambulance')
        actual = target._get_default_civic_route(request)

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
        request = FindServiceRequest(service='urn:nena:service:sos.police')
        actual = target._get_default_civic_route(request)

        self.assertEqual(actual, 'sip:sos@portlandpd.ngesi.maine.gov')

    @patch('lostservice.defaultroutes.defaultroutehandler.DefaultRouteConfigWrapper')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test__get_default_civic_route_civic_matching_override(self, mock_config, mock_db):
        mock_config.settings_for_default_route = MagicMock()
        rules = [
            {
                "name": "some name",
                "conditions": {"A2": "Waldo"},
                "mode": "OverrideRoute",
                "uri": "SIP:+2075555583@strongFD.ngesi.maine.gov"
            },
            {
                "name": "another rule",
                "conditions": {"A2": "Piscataquis"},
                "mode": "ExistingRoute",
                "boundaryid": "{83B81936-29F7-441C-B3F1-5ECE9FA80E50}"
            }
        ]

        default_routes: [DefaultSetting] = [OverrideRouteSetting(DefaultRouteModeEnum.OverrideRoute.value,
                                                                 'urn:nena:service:sos',
                                                                 'sip:sos@oakgrove.ngesi.maine.gov'),
                                            ExistingRouteSetting(DefaultRouteModeEnum.ExistingRoute.value,
                                                                 'urn:nena:service:sos.police',
                                                                 '{AFF10CC6-54F2-4A43-AE12-D8881CD550A4}',
                                                                 mock_db),
                                            CivicMatchingSetting(DefaultRouteModeEnum.CivicMatchingRules.value,
                                                                 'urn:nena:service:sos.fire',
                                                                 rules,
                                                                 mock_db)]

        mock_config.settings_for_default_route.return_value = default_routes

        target = DefaultRouteHandler(mock_config)
        request = FindServiceRequest(location=Location('myID', 'civic', CivicAddress(a2='Waldo')),
                                     service='urn:nena:service:sos.fire')
        actual = target._get_default_civic_route(request)

        self.assertEqual(actual, 'SIP:+2075555583@strongFD.ngesi.maine.gov')

    @patch('lostservice.defaultroutes.defaultroutehandler.DefaultRouteConfigWrapper')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test__get_default_civic_route_civic_matching_existing(self, mock_config, mock_db):
        mock_config.settings_for_default_route = MagicMock()
        rules = [
            {
                "name": "some name",
                "conditions": {"A2": "Waldo"},
                "mode": "OverrideRoute",
                "uri": "SIP:+2075555583@strongFD.ngesi.maine.gov"
            },
            {
                "name": "another rule",
                "conditions": {"A2": "Piscataquis"},
                "mode": "ExistingRoute",
                "boundaryid": "{83B81936-29F7-441C-B3F1-5ECE9FA80E50}"
            }
        ]

        default_routes: [DefaultSetting] = [OverrideRouteSetting(DefaultRouteModeEnum.OverrideRoute.value,
                                                                 'urn:nena:service:sos',
                                                                 'sip:sos@oakgrove.ngesi.maine.gov'),
                                            ExistingRouteSetting(DefaultRouteModeEnum.ExistingRoute.value,
                                                                 'urn:nena:service:sos.police',
                                                                 '{AFF10CC6-54F2-4A43-AE12-D8881CD550A4}',
                                                                 mock_db),
                                            CivicMatchingSetting(DefaultRouteModeEnum.CivicMatchingRules.value,
                                                                 'urn:nena:service:sos.fire',
                                                                 rules,
                                                                 mock_db)]

        mock_config.settings_for_default_route.return_value = default_routes
        mock_db.get_urn_table_mappings = MagicMock()
        mock_db.get_urn_table_mappings.return_value = {'urn:nena:service:sos.fire': 'esbfire'}
        mock_db.get_boundaries_for_previous_id = MagicMock()
        mock_db.get_boundaries_for_previous_id.return_value = [{'routeuri': 'sip:sos@portlandpd.ngesi.maine.gov'}]

        target = DefaultRouteHandler(mock_config)
        request = FindServiceRequest(location=Location('myID', 'civic', CivicAddress(a2='Piscataquis')),
                                     service='urn:nena:service:sos.fire')
        actual = target._get_default_civic_route(request)

        self.assertEqual(actual, 'sip:sos@portlandpd.ngesi.maine.gov')