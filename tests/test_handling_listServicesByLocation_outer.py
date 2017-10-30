import unittest
from unittest.mock import patch
from unittest.mock import MagicMock
import lostservice.handling.core
import lostservice.handling.listServicesByLocation
import lostservice.model.requests
import lostservice.model.responses
import lostservice.model.location

class listServicesByLocationOuterTest(unittest.TestCase):

  @patch('lostservice.handling.listServicesByLocation.ListServiceBYLocationConfigWrapper')
  def test_loop_error(self, mock_config):

        mock_config.source_uri = MagicMock()
        mock_config.source_uri.return_value = 'authoritative.example'

        target = lostservice.handling.listServicesByLocation.ListServiceBylocationOuter(mock_config, None)

        try:
            path = ['authoritative.example']
            target._check_is_loopback(path)
        except Exception as e:
            self.assertEqual(str(e),'<loop message="LoopError" xml:lang="en"/>')

if __name__ == '__main__':
    unittest.main()
