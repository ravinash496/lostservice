import unittest
from unittest.mock import patch
from unittest.mock import MagicMock
import lostservice.handling.findservice
from lostservice.configuration import ConfigurationException


class FindServiceConfigWrapperTest(unittest.TestCase):
    @patch('lostservice.configuration.Configuration')
    def test_find_civic_address_maximum_score_default(self, mock_configuration):
        # should return .05 if there is no default specified in the lostservice.ini
        mock_configuration.get = MagicMock()
        mock_configuration.get.return_value = None
        target = lostservice.handling.findservice.FindServiceConfigWrapper(mock_configuration)
        actual = target.find_civic_address_maximum_score()
        self.assertEqual(actual, .05)

    @patch('lostservice.configuration.Configuration')
    def test_settings_for_default_route_mis_configured_1(self, mock_configuration):
        # default_routing_civic_policy value should be an object
        mock_configuration.get = MagicMock()
        mock_configuration.get.return_value = 'bananas'
        target = lostservice.handling.findservice.FindServiceConfigWrapper(mock_configuration)
        with self.assertRaises(ConfigurationException) as context:
            target.settings_for_default_route()

        base_msg = 'Error in lostservice.ini file. The default_routing_civic_policy setting is mis-configured'
        err_msg = 'The first object name for the default_routing_civic_policy must be default_routes.'
        self.assertTrue('{0} : {1}'.format(base_msg, err_msg) in str(context.exception))

    @patch('lostservice.configuration.Configuration')
    def test_settings_for_default_route_mis_configured_2(self, mock_configuration):
        mock_configuration.get = MagicMock()
        mock_configuration.get.return_value = {'not_named_default_routes': 'no good'}
        target = lostservice.handling.findservice.FindServiceConfigWrapper(mock_configuration)
        with self.assertRaises(ConfigurationException) as context:
            target.settings_for_default_route()

        base_msg = 'Error in lostservice.ini file. The default_routing_civic_policy setting is mis-configured'
        err_msg = 'The first object name for the default_routing_civic_policy must be default_routes.'
        self.assertTrue('{0} : {1}'.format(base_msg, err_msg) in str(context.exception))

    @patch('lostservice.configuration.Configuration')
    def test_settings_for_default_route_mis_configured_3(self, mock_configuration):
        mock_configuration.get = MagicMock()
        mock_configuration.get.return_value = {'default_routes': 'this is not an array'}
        target = lostservice.handling.findservice.FindServiceConfigWrapper(mock_configuration)
        with self.assertRaises(ConfigurationException) as context:
            target.settings_for_default_route()

        base_msg = 'Error in lostservice.ini file. The default_routing_civic_policy setting is mis-configured'
        err_msg = 'The first value must be an array of default route objects.'
        self.assertTrue('{0} : {1}'.format(base_msg, err_msg) in str(context.exception))

    @patch('lostservice.configuration.Configuration')
    def test_settings_for_default_route_mis_configured_4(self, mock_configuration):
        mock_configuration.get = MagicMock()
        mock_configuration.get.return_value = {'default_routes': ['not', 'array', 'of', 'objects']}
        target = lostservice.handling.findservice.FindServiceConfigWrapper(mock_configuration)
        with self.assertRaises(ConfigurationException) as context:
            target.settings_for_default_route()

        base_msg = "Error in lostservice.ini file. The default_routing_civic_policy setting is mis-configured"
        err_msg = 'Each entry in the default_routes array must be an object.'
        self.assertTrue('{0} : {1}'.format(base_msg, err_msg) in str(context.exception))

    @patch('lostservice.configuration.Configuration')
    def test_settings_for_default_route_mis_configured_5(self, mock_configuration):
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
        target = lostservice.handling.findservice.FindServiceConfigWrapper(mock_configuration)
        with self.assertRaises(ConfigurationException) as context:
            target.settings_for_default_route()

        base_msg = "Error in lostservice.ini file. The default_routing_civic_policy setting is mis-configured"
        err_msg = 'You must specify the mode for each item.'
        self.assertTrue('{0} : {1}'.format(base_msg, err_msg) in str(context.exception))

    @patch('lostservice.configuration.Configuration')
    def test_settings_for_default_route_mis_configured_6(self, mock_configuration):
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
        target = lostservice.handling.findservice.FindServiceConfigWrapper(mock_configuration)
        with self.assertRaises(ConfigurationException) as context:
            target.settings_for_default_route()

        base_msg = "Error in lostservice.ini file. The default_routing_civic_policy setting is mis-configured"
        err_msg = 'Unsupported mode: invalid_mode'
        self.assertTrue('{0} : {1}'.format(base_msg, err_msg) in str(context.exception))

    @patch('lostservice.configuration.Configuration')
    def test_settings_for_default_route_mis_configured_7(self, mock_configuration):
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
        target = lostservice.handling.findservice.FindServiceConfigWrapper(mock_configuration)
        with self.assertRaises(ConfigurationException) as context:
            target.settings_for_default_route()

        base_msg = "Error in lostservice.ini file. The default_routing_civic_policy setting is mis-configured"
        err_msg = 'You must specify the urn for each item.'
        self.assertTrue('{0} : {1}'.format(base_msg, err_msg) in str(context.exception))

    @patch('lostservice.configuration.Configuration')
    def test_settings_for_default_route_mis_configured_8(self, mock_configuration):
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
        target = lostservice.handling.findservice.FindServiceConfigWrapper(mock_configuration)
        with self.assertRaises(ConfigurationException) as context:
            target.settings_for_default_route()

        base_msg = "Error in lostservice.ini file. The default_routing_civic_policy setting is mis-configured"
        err_msg = 'You must specify the uri for each item.'
        self.assertTrue('{0} : {1}'.format(base_msg, err_msg) in str(context.exception))


if __name__ == '__main__':
    unittest.main()
