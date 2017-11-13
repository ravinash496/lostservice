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


if __name__ == '__main__':
    unittest.main()
