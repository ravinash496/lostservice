#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from unittest.mock import patch
from unittest.mock import MagicMock
from lostservice.defaultroutes.defaultroutehandler import DefaultRouteConfigWrapper, OverrideRouteSetting, \
    ExistingRouteSetting, CivicMatchingSetting, CivicMatchingRule, CivicExistingMatchingRule, \
    CivicOverrideMatchingRule
from lostservice.configuration import ConfigurationException
from typing import List


class DefaultRouteConfigWrapperTest(unittest.TestCase):

    base_msg = 'Error in lostservice.ini file. The default_routing_civic_policy setting is mis-configured.'
    @patch('lostservice.configuration.Configuration')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_settings_for_default_route_mis_configured_1(self, mock_configuration, mock_db):
        # default_routing_civic_policy value should be an object
        mock_configuration.get = MagicMock()
        mock_configuration.get.return_value = 'bananas'
        target = DefaultRouteConfigWrapper(mock_configuration, mock_db)
        with self.assertRaises(ConfigurationException) as context:
            target.settings_for_default_route()

        err_msg = 'The first object name for the default_routing_civic_policy must be default_routes.'
        self.assertTrue('{0} : {1}'.format(self.base_msg, err_msg) in str(context.exception))

    @patch('lostservice.configuration.Configuration')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_settings_for_default_route_mis_configured_2(self, mock_configuration, mock_db):
        mock_configuration.get = MagicMock()
        mock_configuration.get.return_value = {'not_named_default_routes': 'no good'}
        target = DefaultRouteConfigWrapper(mock_configuration, mock_db)
        with self.assertRaises(ConfigurationException) as context:
            target.settings_for_default_route()

        err_msg = 'The first object name for the default_routing_civic_policy must be default_routes.'
        self.assertTrue('{0} : {1}'.format(self.base_msg, err_msg) in str(context.exception))

    @patch('lostservice.configuration.Configuration')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_settings_for_default_route_mis_configured_3(self, mock_configuration, mock_db):
        mock_configuration.get = MagicMock()
        mock_configuration.get.return_value = {'default_routes': 'this is not an array'}
        target = DefaultRouteConfigWrapper(mock_configuration, mock_db)
        with self.assertRaises(ConfigurationException) as context:
            target.settings_for_default_route()

        err_msg = 'The first value must be an array of default route objects.'
        self.assertTrue('{0} : {1}'.format(self.base_msg, err_msg) in str(context.exception))

    @patch('lostservice.configuration.Configuration')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_settings_for_default_route_mis_configured_4(self, mock_configuration, mock_db):
        mock_configuration.get = MagicMock()
        mock_configuration.get.return_value = {'default_routes': ['not', 'array', 'of', 'objects']}
        target = DefaultRouteConfigWrapper(mock_configuration, mock_db)
        with self.assertRaises(ConfigurationException) as context:
            target.settings_for_default_route()

        err_msg = 'Each entry in the default_routes array must be an object.'
        self.assertTrue('{0} : {1}'.format(self.base_msg, err_msg) in str(context.exception))

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
        target = DefaultRouteConfigWrapper(mock_configuration, mock_db)
        with self.assertRaises(ConfigurationException) as context:
            target.settings_for_default_route()

        err_msg = 'You must specify the mode for each item.'
        self.assertTrue('{0} : {1}'.format(self.base_msg, err_msg) in str(context.exception))

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
        target = DefaultRouteConfigWrapper(mock_configuration, mock_db)
        with self.assertRaises(ConfigurationException) as context:
            target.settings_for_default_route()

        err_msg = 'Unsupported mode: invalid_mode'
        self.assertTrue('{0} : {1}'.format(self.base_msg, err_msg) in str(context.exception))

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
        target = DefaultRouteConfigWrapper(mock_configuration, mock_db)
        with self.assertRaises(ConfigurationException) as context:
            target.settings_for_default_route()

        err_msg = 'You must specify the urn for each item.'
        self.assertTrue('{0} : {1}'.format(self.base_msg, err_msg) in str(context.exception))

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
        target = DefaultRouteConfigWrapper(mock_configuration, mock_db)
        with self.assertRaises(ConfigurationException) as context:
            target.settings_for_default_route()

        err_msg = 'You must specify the uri for each item that is in OverrideRoute mode.'
        self.assertTrue('{0} : {1}'.format(self.base_msg, err_msg) in str(context.exception))

    @patch('lostservice.configuration.Configuration')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_settings_for_default_route_mis_configured_9(self, mock_configuration, mock_db):
        mock_configuration.get = MagicMock()
        # 3rd key should be boundaryid when the mode is ExistingRoute
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
        target = DefaultRouteConfigWrapper(mock_configuration, mock_db)
        with self.assertRaises(ConfigurationException) as context:
            target.settings_for_default_route()

        err_msg = 'You must specify the boundaryid for each item that is in ExistingRoute mode.'
        self.assertTrue('{0} : {1}'.format(self.base_msg, err_msg) in str(context.exception))

    @patch('lostservice.configuration.Configuration')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_settings_for_default_route_mis_configured_10(self, mock_configuration, mock_db):
        mock_configuration.get = MagicMock()
        # Need a rules key when the mode is CivicMatchingRules
        mock_configuration.get.return_value = {
            'default_routes': [
                {
                    "mode": "CivicMatchingRules",
                    "urn": "urn.nena:service:sos.fire",
                    "uri": "should be a list of rules here"
                }
            ]
        }
        target = DefaultRouteConfigWrapper(mock_configuration, mock_db)
        with self.assertRaises(ConfigurationException) as context:
            target.settings_for_default_route()

        err_msg = 'You must specify the rules for each item that is in CivicMatchingRules mode.'
        self.assertTrue('{0} : {1}'.format(self.base_msg, err_msg) in str(context.exception))

    @patch('lostservice.configuration.Configuration')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_settings_for_default_route_mis_configured_11(self, mock_configuration, mock_db):
        mock_configuration.get = MagicMock()
        # rules element value must be a list
        mock_configuration.get.return_value = {
            'default_routes': [
                {
                    "mode": "CivicMatchingRules",
                    "urn": "urn.nena:service:sos.fire",
                    "rules": "should be a list of rules here"
                }
            ]
        }
        target = DefaultRouteConfigWrapper(mock_configuration, mock_db)
        with self.assertRaises(ConfigurationException) as context:
            target.settings_for_default_route()

        err_msg = 'The rules element value must be an array of rules.'
        self.assertTrue('{0} : {1}'.format(self.base_msg, err_msg) in str(context.exception))

    @patch('lostservice.configuration.Configuration')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_settings_for_default_route_mis_configured_12(self, mock_configuration, mock_db):
        mock_configuration.get = MagicMock()
        # rules must contain dictionary of key values
        mock_configuration.get.return_value = {
            'default_routes': [
                {
                    "mode": "CivicMatchingRules",
                    "urn": "urn.nena:service:sos.fire",
                    "rules": [
                        "this", "aint", "a", "list", "of", "dictionary"
                    ]
                }
            ]
        }
        target = DefaultRouteConfigWrapper(mock_configuration, mock_db)
        with self.assertRaises(ConfigurationException) as context:
            target.settings_for_default_route()

        err_msg = 'Each rule in rules must be a dictionary of key value pairs.'
        self.assertTrue('{0} : {1}'.format(self.base_msg, err_msg) in str(context.exception))

    @patch('lostservice.configuration.Configuration')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_settings_for_default_route_mis_configured_13(self, mock_configuration, mock_db):
        mock_configuration.get = MagicMock()
        # Each rule must contain a name element
        mock_configuration.get.return_value = {
            'default_routes': [
                {
                    "mode": "CivicMatchingRules",
                    "urn": "urn.nena:service:sos.fire",
                    "rules": [
                        {
                            "oops": "some name",
                            "conditions": [
                                {
                                    "field": "A2",
                                    "value": "Waldo"
                                }
                            ],
                            "mode": "OverrideRoute",
                            "uri": "SIP:+2075555583@strongFD.ngesi.maine.gov"
                        },
                        {
                            "name": "another rule",
                            "conditions": [
                                {
                                    "field": "A2",
                                    "value": "Piscataquis"
                                }
                            ],
                            "mode": "ExistingRoute",
                            "boundaryid": "{83B81936-29F7-441C-B3F1-5ECE9FA80E50}"
                        }
                    ]
                }
            ]
        }
        target = DefaultRouteConfigWrapper(mock_configuration, mock_db)
        with self.assertRaises(ConfigurationException) as context:
            target.settings_for_default_route()

        err_msg = 'Each rule must have a name element.'
        self.assertTrue('{0} : {1}'.format(self.base_msg, err_msg) in str(context.exception))

    @patch('lostservice.configuration.Configuration')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_settings_for_default_route_mis_configured_14(self, mock_configuration, mock_db):
        mock_configuration.get = MagicMock()
        # Each rule must contain a conditions element
        mock_configuration.get.return_value = {
            'default_routes': [
                {
                    "mode": "CivicMatchingRules",
                    "urn": "urn.nena:service:sos.fire",
                    "rules": [
                        {
                            "name": "some name",
                            "oops": [
                                {
                                    "field": "A2",
                                    "value": "Waldo"
                                }
                            ],
                            "mode": "OverrideRoute",
                            "uri": "SIP:+2075555583@strongFD.ngesi.maine.gov"
                        },
                        {
                            "name": "another rule",
                            "conditions": [
                                {
                                    "field": "A2",
                                    "value": "Piscataquis"
                                }
                            ],
                            "mode": "ExistingRoute",
                            "boundaryid": "{83B81936-29F7-441C-B3F1-5ECE9FA80E50}"
                        }
                    ]
                }
            ]
        }
        target = DefaultRouteConfigWrapper(mock_configuration, mock_db)
        with self.assertRaises(ConfigurationException) as context:
            target.settings_for_default_route()

        err_msg = 'Each rule must have a conditions element.'
        self.assertTrue('{0} : {1}'.format(self.base_msg, err_msg) in str(context.exception))

    @patch('lostservice.configuration.Configuration')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_settings_for_default_route_mis_configured_15(self, mock_configuration, mock_db):
        mock_configuration.get = MagicMock()
        # Each rule must contain a conditions element
        mock_configuration.get.return_value = {
            'default_routes': [
                {
                    "mode": "CivicMatchingRules",
                    "urn": "urn.nena:service:sos.fire",
                    "rules": [
                        {
                            "name": "some name",
                            "conditions": [
                                {
                                    "field": "A2",
                                    "value": "Waldo"
                                }
                            ],
                            "oops": "OverrideRoute",
                            "uri": "SIP:+2075555583@strongFD.ngesi.maine.gov"
                        },
                        {
                            "name": "another rule",
                            "conditions": [
                                {
                                    "field": "A2",
                                    "value": "Piscataquis"
                                }
                            ],
                            "mode": "ExistingRoute",
                            "boundaryid": "{83B81936-29F7-441C-B3F1-5ECE9FA80E50}"
                        }
                    ]
                }
            ]
        }
        target = DefaultRouteConfigWrapper(mock_configuration, mock_db)
        with self.assertRaises(ConfigurationException) as context:
            target.settings_for_default_route()

        err_msg = 'Each rule must have a mode element.'
        self.assertTrue('{0} : {1}'.format(self.base_msg, err_msg) in str(context.exception))

    @patch('lostservice.configuration.Configuration')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_settings_for_default_route_mis_configured_16(self, mock_configuration, mock_db):
        mock_configuration.get = MagicMock()
        # Each rule where mode is OverrideRoute must have a uri element.
        mock_configuration.get.return_value = {
            'default_routes': [
                {
                    "mode": "CivicMatchingRules",
                    "urn": "urn.nena:service:sos.fire",
                    "rules": [
                        {
                            "name": "some name",
                            "conditions": [
                                {
                                    "field": "A2",
                                    "value": "Waldo"
                                }
                            ],
                            "mode": "OverrideRoute",
                            "oops": "SIP:+2075555583@strongFD.ngesi.maine.gov"
                        },
                        {
                            "name": "another rule",
                            "conditions": [
                                {
                                    "field": "A2",
                                    "value": "Piscataquis"
                                }
                            ],
                            "mode": "ExistingRoute",
                            "boundaryid": "{83B81936-29F7-441C-B3F1-5ECE9FA80E50}"
                        }
                    ]
                }
            ]
        }
        target = DefaultRouteConfigWrapper(mock_configuration, mock_db)
        with self.assertRaises(ConfigurationException) as context:
            target.settings_for_default_route()

        err_msg = 'Each rule where mode is OverrideRoute must have a uri element.'
        self.assertTrue('{0} : {1}'.format(self.base_msg, err_msg) in str(context.exception))

    @patch('lostservice.configuration.Configuration')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_settings_for_default_route_mis_configured_17(self, mock_configuration, mock_db):
        mock_configuration.get = MagicMock()
        # Each rule where mode is ExistingRoute must have a boundaryid element.
        mock_configuration.get.return_value = {
            'default_routes': [
                {
                    "mode": "CivicMatchingRules",
                    "urn": "urn.nena:service:sos.fire",
                    "rules": [
                        {
                            "name": "some name",
                            "conditions": [
                                {
                                    "field": "A2",
                                    "value": "Waldo"
                                }
                            ],
                            "mode": "OverrideRoute",
                            "uri": "SIP:+2075555583@strongFD.ngesi.maine.gov"
                        },
                        {
                            "name": "another rule",
                            "conditions": [
                                {
                                    "field": "A2",
                                    "value": "Piscataquis"
                                }
                            ],
                            "mode": "ExistingRoute",
                            "oops": "{83B81936-29F7-441C-B3F1-5ECE9FA80E50}"
                        }
                    ]
                }
            ]
        }
        target = DefaultRouteConfigWrapper(mock_configuration, mock_db)
        with self.assertRaises(ConfigurationException) as context:
            target.settings_for_default_route()

        err_msg = 'Each rule where mode is ExistingRoute must have a boundaryid element.'
        self.assertTrue('{0} : {1}'.format(self.base_msg, err_msg) in str(context.exception))

    @patch('lostservice.configuration.Configuration')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_settings_for_default_route_mis_configured_18(self, mock_configuration, mock_db):
        mock_configuration.get = MagicMock()
        # Each rule's mode must be either 'OverrideRoute' or 'ExistingRoute'.
        mock_configuration.get.return_value = {
            'default_routes': [
                {
                    "mode": "CivicMatchingRules",
                    "urn": "urn.nena:service:sos.fire",
                    "rules": [
                        {
                            "name": "some name",
                            "conditions": [
                                {
                                    "field": "A2",
                                    "value": "Waldo"
                                }
                            ],
                            "mode": "ooops",
                            "uri": "SIP:+2075555583@strongFD.ngesi.maine.gov"
                        },
                        {
                            "name": "another rule",
                            "conditions": [
                                {
                                    "field": "A2",
                                    "value": "Piscataquis"
                                }
                            ],
                            "mode": "ExistingRoute",
                            "boundaryid": "{83B81936-29F7-441C-B3F1-5ECE9FA80E50}"
                        }
                    ]
                }
            ]
        }
        target = DefaultRouteConfigWrapper(mock_configuration, mock_db)
        with self.assertRaises(ConfigurationException) as context:
            target.settings_for_default_route()

        err_msg = 'Only modes of "OverrideRoute" or "ExistingRoute"' \
                  'are supported for civic address rule types.'
        self.assertTrue('{0} : {1}'.format(self.base_msg, err_msg) in str(context.exception))

    @patch('lostservice.configuration.Configuration')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_settings_for_default_route_ok(self, mock_configuration, mock_db):
        mock_configuration.get = MagicMock()
        # test settings_for_default_route returns correct objects
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
              },
              {
                "mode": "CivicMatchingRules",
                "urn": "urn.nena:service:sos.fire",
                "rules": [
                   {
                       "name": "some name",
                       "conditions": [
                           {
                               "field": "A2",
                               "value": "Waldo"
                           }
                       ],
                       "mode": "OverrideRoute",
                       "uri": "SIP:+2075555583@strongFD.ngesi.maine.gov"
                   },
                   {
                       "name": "another rule",
                       "conditions": [
                           {
                               "field": "A2",
                               "value": "Piscataquis"
                           }
                       ],
                       "mode": "ExistingRoute",
                       "boundaryid": "{83B81936-29F7-441C-B3F1-5ECE9FA80E50}"
                   }
                ]
              }
           ]
        }
        target = DefaultRouteConfigWrapper(mock_configuration, mock_db)
        result = target.settings_for_default_route()

        self.assertTrue(isinstance(result, list), "Result must be a list.")
        self.assertTrue(len(result) == 3, "Result must be a list with three settings in it.")
        self.assertTrue(isinstance(result[0], OverrideRouteSetting), "1st object should be a OverrideRouteSetting")
        self.assertTrue(isinstance(result[1], ExistingRouteSetting), "2nd object should be a ExistingRouteSetting")
        self.assertTrue(isinstance(result[2], CivicMatchingSetting), "3rd object should be a CivicMatchingSetting")
        civic_matching_setting: CivicMatchingSetting = result[2]
        self.assertTrue(len(civic_matching_setting.rules) == 2)
        self.assertTrue(isinstance(civic_matching_setting.rules[0],
                                   CivicMatchingRule), "Should be a CiviMatchingRule")
        matching_rule = civic_matching_setting.rules[0]
        self.assertTrue(isinstance(matching_rule, CivicOverrideMatchingRule))
        matching_rule = civic_matching_setting.rules[1]
        self.assertTrue(isinstance(matching_rule, CivicExistingMatchingRule))


if __name__ == '__main__':
    unittest.main()
