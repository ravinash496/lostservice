#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from unittest.mock import patch
from unittest.mock import MagicMock
import lostservice.defaultroutes.defaultroutehandler
from lostservice.configuration import ConfigurationException


class DefaultRouteConfigWrapperTest(unittest.TestCase):

    @patch('lostservice.configuration.Configuration')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_settings_for_default_route_mis_configured_1(self, mock_configuration, mock_db):
        # default_routing_civic_policy value should be an object
        mock_configuration.get = MagicMock()
        mock_configuration.get.return_value = 'bananas'
        target = lostservice.defaultroutes.defaultroutehandler.DefaultRouteConfigWrapper(mock_configuration, mock_db)
        with self.assertRaises(ConfigurationException) as context:
            target.settings_for_default_route()

        base_msg = 'Error in lostservice.ini file. The default_routing_civic_policy setting is mis-configured'
        err_msg = 'The first object name for the default_routing_civic_policy must be default_routes.'
        self.assertTrue('{0} : {1}'.format(base_msg, err_msg) in str(context.exception))

    @patch('lostservice.configuration.Configuration')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_settings_for_default_route_mis_configured_2(self, mock_configuration, mock_db):
        mock_configuration.get = MagicMock()
        mock_configuration.get.return_value = {'not_named_default_routes': 'no good'}
        target = lostservice.defaultroutes.defaultroutehandler.DefaultRouteConfigWrapper(mock_configuration, mock_db)
        with self.assertRaises(ConfigurationException) as context:
            target.settings_for_default_route()

        base_msg = 'Error in lostservice.ini file. The default_routing_civic_policy setting is mis-configured'
        err_msg = 'The first object name for the default_routing_civic_policy must be default_routes.'
        self.assertTrue('{0} : {1}'.format(base_msg, err_msg) in str(context.exception))

    @patch('lostservice.configuration.Configuration')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_settings_for_default_route_mis_configured_3(self, mock_configuration, mock_db):
        mock_configuration.get = MagicMock()
        mock_configuration.get.return_value = {'default_routes': 'this is not an array'}
        target = lostservice.defaultroutes.defaultroutehandler.DefaultRouteConfigWrapper(mock_configuration, mock_db)
        with self.assertRaises(ConfigurationException) as context:
            target.settings_for_default_route()

        base_msg = 'Error in lostservice.ini file. The default_routing_civic_policy setting is mis-configured'
        err_msg = 'The first value must be an array of default route objects.'
        self.assertTrue('{0} : {1}'.format(base_msg, err_msg) in str(context.exception))

    @patch('lostservice.configuration.Configuration')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_settings_for_default_route_mis_configured_4(self, mock_configuration, mock_db):
        mock_configuration.get = MagicMock()
        mock_configuration.get.return_value = {'default_routes': ['not', 'array', 'of', 'objects']}
        target = lostservice.defaultroutes.defaultroutehandler.DefaultRouteConfigWrapper(mock_configuration, mock_db)
        with self.assertRaises(ConfigurationException) as context:
            target.settings_for_default_route()

        base_msg = "Error in lostservice.ini file. The default_routing_civic_policy setting is mis-configured"
        err_msg = 'Each entry in the default_routes array must be an object.'
        self.assertTrue('{0} : {1}'.format(base_msg, err_msg) in str(context.exception))

    @patch('lostservice.configuration.Configuration')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_settings_for_default_route_mis_configured_5(self, mock_configuration, mock_db):
        mock_configuration.get = MagicMock()
        # first key in setting is mis-spelled
        mock_configuration.get.return_value = {
           'default_routes': [
              {
                 'moaud': 'OverrideRoute',
                 'urn': 'urn:nena:service:sos',
                 'uri': 'sip:sos@oakgrove.ngesi.maine.gov'
              },
              {
                 'mode': 'OverrideRoute',
                 'urn': ' urn:nena:service:sos.police',
                 'uri': 'sip:sos@portlandpd.ngesi.maine.gov'
              }
           ]
            }
        target = lostservice.defaultroutes.defaultroutehandler.DefaultRouteConfigWrapper(mock_configuration, mock_db)
        with self.assertRaises(ConfigurationException) as context:
            target.settings_for_default_route()

        base_msg = "Error in lostservice.ini file. The default_routing_civic_policy setting is mis-configured"
        err_msg = 'You must specify the mode for each item.'
        self.assertTrue('{0} : {1}'.format(base_msg, err_msg) in str(context.exception))

    @patch('lostservice.configuration.Configuration')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_settings_for_default_route_mis_configured_6(self, mock_configuration, mock_db):
        mock_configuration.get = MagicMock()
        # first key in setting is mis-spelled
        mock_configuration.get.return_value = {
           'default_routes': [
              {
                 'mode': 'invalid_mode',
                 'urn': 'urn:nena:service:sos',
                 'uri': 'sip:sos@oakgrove.ngesi.maine.gov'
              },
              {
                 'mode': 'OverrideRoute',
                 'urn': ' urn:nena:service:sos.police',
                 'uri': 'sip:sos@portlandpd.ngesi.maine.gov'
              }
           ]
            }
        target = lostservice.defaultroutes.defaultroutehandler.DefaultRouteConfigWrapper(mock_configuration, mock_db)
        with self.assertRaises(ConfigurationException) as context:
            target.settings_for_default_route()

        base_msg = "Error in lostservice.ini file. The default_routing_civic_policy setting is mis-configured"
        err_msg = 'Unsupported mode: invalid_mode'
        self.assertTrue('{0} : {1}'.format(base_msg, err_msg) in str(context.exception))

    @patch('lostservice.configuration.Configuration')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_settings_for_default_route_mis_configured_7(self, mock_configuration, mock_db):
        mock_configuration.get = MagicMock()
        # 2nd key in setting is mis-spelled
        mock_configuration.get.return_value = {
           'default_routes': [
              {
                 'mode': 'OverrideRoute',
                 'urn': 'urn:nena:service:sos',
                 'uri': 'sip:sos@oakgrove.ngesi.maine.gov'
              },
              {
                 'mode': 'OverrideRoute',
                 'urine': ' urn:nena:service:sos.police',
                 'uri': 'sip:sos@portlandpd.ngesi.maine.gov'
              }
           ]
            }
        target = lostservice.defaultroutes.defaultroutehandler.DefaultRouteConfigWrapper(mock_configuration, mock_db)
        with self.assertRaises(ConfigurationException) as context:
            target.settings_for_default_route()

        base_msg = "Error in lostservice.ini file. The default_routing_civic_policy setting is mis-configured"
        err_msg = 'You must specify the urn for each item.'
        self.assertTrue('{0} : {1}'.format(base_msg, err_msg) in str(context.exception))

    @patch('lostservice.configuration.Configuration')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_settings_for_default_route_mis_configured_8(self, mock_configuration, mock_db):
        mock_configuration.get = MagicMock()
        # 3rd key in setting is mis-spelled
        mock_configuration.get.return_value = {
           'default_routes': [
              {
                 'mode': 'OverrideRoute',
                 'urn': 'urn:nena:service:sos',
                 'uri': 'sip:sos@oakgrove.ngesi.maine.gov'
              },
              {
                 'mode': 'OverrideRoute',
                 'urn': ' urn:nena:service:sos.police',
                 'uright': 'sip:sos@portlandpd.ngesi.maine.gov'
              }
           ]
            }
        target = lostservice.defaultroutes.defaultroutehandler.DefaultRouteConfigWrapper(mock_configuration, mock_db)
        with self.assertRaises(ConfigurationException) as context:
            target.settings_for_default_route()

        base_msg = "Error in lostservice.ini file. The default_routing_civic_policy setting is mis-configured"
        err_msg = 'You must specify the uri for each item that is in OverrideRoute mode.'
        self.assertTrue('{0} : {1}'.format(base_msg, err_msg) in str(context.exception))

    @patch('lostservice.configuration.Configuration')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_settings_for_default_route_mis_configured_9(self, mock_configuration, mock_db):
        mock_configuration.get = MagicMock()
        # 3rd key in setting is mis-spelled
        mock_configuration.get.return_value = {
            'default_routes': [
                {
                    'mode': 'OverrideRoute',
                    'urn': 'urn:nena:service:sos',
                    'uri': 'sip:sos@oakgrove.ngesi.maine.gov'
                },
                {
                    'mode': 'ExistingRoute',
                    'urn': ' urn:nena:service:sos.police',
                    'uri': 'sip:sos@portlandpd.ngesi.maine.gov'
                }
            ]
        }
        target = lostservice.defaultroutes.defaultroutehandler.DefaultRouteConfigWrapper(mock_configuration, mock_db)
        with self.assertRaises(ConfigurationException) as context:
            target.settings_for_default_route()

        base_msg = "Error in lostservice.ini file. The default_routing_civic_policy setting is mis-configured"
        err_msg = 'You must specify the boundaryid for each item that is in ExistingRoute mode.'
        self.assertTrue('{0} : {1}'.format(base_msg, err_msg) in str(context.exception))

    @patch('lostservice.configuration.Configuration')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_settings_for_default_route_ok(self, mock_configuration, mock_db):
        mock_configuration.get = MagicMock()
        # first key in setting is mis-spelled
        mock_configuration.get.return_value = {
           'default_routes': [
              {
                 'mode': 'OverrideRoute',
                 'urn': 'urn:nena:service:sos',
                 'uri': 'sip:sos@oakgrove.ngesi.maine.gov'
              },
              {
                 'mode': 'ExistingRoute',
                 'urn': ' urn:nena:service:sos.police',
                 'boundaryid': '{AFF10CC6-54F2-4A43-AE12-D8881CD550A4}'
              }
           ]
            }
        target = lostservice.defaultroutes.defaultroutehandler.DefaultRouteConfigWrapper(mock_configuration, mock_db)
        result = target.settings_for_default_route()

        self.assertTrue(isinstance(result, list), "Result must be a list.")
        self.assertTrue(len(result) == 2, "Result must be a list with two settings in it.")


if __name__ == '__main__':
    unittest.main()
