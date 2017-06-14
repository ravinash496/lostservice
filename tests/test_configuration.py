import unittest
import os
import lostservice.configuration as config
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
        self.assertEqual(self._default_ini_file, self._config.default_config_file)

    def test_get_sections(self):
        expected = ['Database', 'SectionOne', 'Section Two', 'Section2', 'Section3', 'Section4']
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

    def test_set_new_section(self):
        self._config.set_option('section', 'option', 'value')
        self.assertTrue('section' in self._config.get_sections())
        self.assertTrue('option' in self._config.get_options('section'))
        self.assertEqual('value', self._config.get('section', 'option'))

    def test_set_existing_section(self):
        self._config.set_option('SectionOne', 'optionx', 'valuex')
        self.assertTrue('optionx' in self._config.get_options('SectionOne'))
        self.assertEqual('valuex', self._config.get('SectionOne', 'optionx'))

    def test_load_from_passed_file(self):
        custom_ini_file = os.path.join(os.path.dirname(__file__), './config/test.ini')
        target = Configuration(custom_config=custom_ini_file)
        expected = 'postgresql://squidward:sandy@spongebob:1111/patrick'
        actual = target.get_db_connection_string()
        self.assertEqual(expected, actual)

    def test_load_from_env_file(self):
        custom_ini_file = os.path.join(os.path.dirname(__file__), './config/test.ini')
        os.environ[config._CONFIGFILE] = custom_ini_file
        target = Configuration()
        expected = 'postgresql://squidward:sandy@spongebob:1111/patrick'
        actual = target.get_db_connection_string()
        self.assertEqual(expected, actual)
        os.environ.pop(config._CONFIGFILE)

    def test_load_from_env_values(self):
        custom_ini_file = os.path.join(os.path.dirname(__file__), './config/test.ini')
        os.environ[config._CONFIGFILE] = custom_ini_file
        os.environ[config._DBHOSTNAME] = 'DBHOSTNAME'
        os.environ[config._DBPORT] = 'DBPORT'
        os.environ[config._DBNAME] = 'DBNAME'
        os.environ[config._DBUSER] = 'DBUSER'
        os.environ[config._DBPASSWORD] = 'DBPASSWORD'

        target = Configuration()
        expected = 'postgresql://DBUSER:DBPASSWORD@DBHOSTNAME:DBPORT/DBNAME'
        actual = target.get_db_connection_string()
        self.assertEqual(expected, actual)

        os.environ.pop(config._CONFIGFILE)
        os.environ.pop(config._DBHOSTNAME)
        os.environ.pop(config._DBPORT)
        os.environ.pop(config._DBNAME)
        os.environ.pop(config._DBUSER)
        os.environ.pop(config._DBPASSWORD)

    def test_load_fail(self):
        with self.assertRaises(ConfigurationException):
            target = Configuration()

        
if __name__ == '__main__':
    unittest.main()

