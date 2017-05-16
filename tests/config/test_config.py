import unittest
import os
import lostservice.configuration as globalconfig
from lostservice.configuration import Configuration

class ConfigurationTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(ConfigurationTest, self).__init__(*args, **kwargs)
        self._ini_file = os.path.join(os.path.dirname(__file__), 'test.ini')
        self._config = None

    def setUp(self):
        super(ConfigurationTest, self).setUp()
        self._config = Configuration(self._ini_file)

    def tearDown(self):
        super(ConfigurationTest, self).tearDown()
        self._config = None

    def test_init(self):
        self.assertEqual(self._ini_file, self._config.file)

    def test_global(self):
        globalconfig.set(self._config)
        theglobalconfig = globalconfig.get()
        self.assertTrue(theglobalconfig is self._config)

    def test_get_sections(self):
        expected = ['SectionOne', 'Section Two', 'Section3']
        actual = self._config.get_sections()
        self.assertListEqual(expected, actual)

    def test_get_options(self):
        expected = ['value_one', 'value_two']
        actual = self._config.get_options('SectionOne')
        self.assertListEqual(expected, actual)

    def test_get_option_as_value_required(self):
        actual = self._config.get('SectionOne', 'value_one')
        self.assertEqual('foo', actual)

    def test_same_name_different_section(self):
        actual = self._config.get('Section3', 'value_one')
        self.assertEqual('whatever', actual)

        
if __name__ == '__main__':
    unittest.main()

