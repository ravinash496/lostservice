import unittest
import os
import lostservice.configuration as globalconfig
from lostservice.configuration import Configuration, ConfigurationException

class ConfigurationTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(ConfigurationTest, self).__init__(*args, **kwargs)
        self._custom_ini_file = os.path.join(os.path.dirname(__file__), './config/test.ini')
        self._default_ini_file = os.path.join(os.path.dirname(__file__), './config/test.default.ini')
        self._config = None

    def setUp(self):
        super(ConfigurationTest, self).setUp()
        self._config = Configuration(self._custom_ini_file)

    def tearDown(self):
        super(ConfigurationTest, self).tearDown()
        self._config = None

    def test_init(self):
        self.assertEqual(self._custom_ini_file, self._config.custom_config_file)
        self.assertEquals(self._default_ini_file, self._config.default_config_file)

    def test_global(self):
        globalconfig.set_config(self._config)
        theglobalconfig = globalconfig.get_config()
        self.assertTrue(theglobalconfig is self._config)

    def test_get_sections(self):
        expected = ['SectionOne', 'Section Two', 'Section2', 'Section3', 'Section4']
        actual = self._config.get_sections()
        expected.sort()
        actual.sort()
        self.assertListEqual(expected, actual)

    def test_get_options(self):
        expected = ['value_one', 'value_two']
        actual = self._config.get_options('SectionOne')
        expected.sort()
        actual.sort()
        self.assertListEqual(expected, actual)

    def test_get_options_bad_section(self):
        with self.assertRaises(ConfigurationException):
            actual = self._config.get_options('ChemicalX')

    def test_get_option_as_value_required(self):
        actual = self._config.get('SectionOne', 'value_one')
        self.assertEqual('foo', actual)

    def test_same_name_different_section(self):
        actual = self._config.get('Section2', 'value_one')
        self.assertEqual('fubar', actual)

    def test_get_option_from_default(self):
        actual = self._config.get('Section4', 'anoption')
        self.assertEqual('do not touch', actual)

    def test_get_override(self):
        actual = self._config.get('Section3', 'value_one')
        self.assertEqual('whatever', actual)

    def test_get_not_required(self):
        # Test for non-existent section.
        actual = self._config.get("ChemicalX", 'Bubbles', required=False)
        self.assertIsNone(actual)
        # Test for section that exists but no option.
        actual = self._config.get('SectionOne', 'Bubbles', required=False)
        self.assertIsNone(actual)

    def test_get_as_object(self):
        expected = { 'foo': 'bar', 'bas': 'zed'}
        actual = self._config.get('Section Two', 'some_values', as_object=True)
        self.assertDictEqual(expected, actual)


        
if __name__ == '__main__':
    unittest.main()

