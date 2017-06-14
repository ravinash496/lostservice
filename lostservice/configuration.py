#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: configuration
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

Configuration related classes and functions.
"""

import os
import configparser
from enum import Enum

_DBHOSTNAME = 'DBHOSTNAME'
_DBPORT = 'DBPORT'
_DBNAME = 'DBNAME'
_DBUSER = 'DBUSER'
_DBPASSWORD = 'DBPASSWORD'
_CONFIGFILE = 'CONFIGFILE'
_LOGFILE = 'LOGFILE'
_SOURCE_URI = 'SOURCE_URI'
_LAST_UPDATE_FIELD = 'LAST_UPDATE_FIELD'
_SERVICE_EXPIRES_POLICY = 'SERVICE_EXPIRES_POLICY'
_SERVICE_EXPIRES_TIMESPAN = 'SERVIC_EXPIRES_TIMESPAN'


class ConfigurationException(Exception):
    """
    Something went wrong while loading, retrieving, or setting configuration
    values.
    """
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super(ConfigurationException, self).__init__(message)


class ServiceExpiresPolicyEnum(Enum):
    NoCache = 1
    NoExpiration = 2
    TimeSpan = 3


class Configuration(object):
    """
    A wrapper for reading from and writing to a configuration file.

    """
    
    def __init__(self, custom_config=None, default_config=None):
        """
        Constructor

        :param custom_config: The full path to the public/user/custom configuration (.ini) file.
        :type custom_config: ``str``
        :param default_config: The full path to the default configuration file.
        :type default_config: ``str``
        """
        super(Configuration, self).__init__()

        self._custom_config = custom_config
        self._default_config = default_config

        # If nothing was passed in, we're going to look in the environment.
        if self._custom_config is None:
            self._custom_config = os.getenv(_CONFIGFILE)

        # Still nothing?  Bail.
        if self._custom_config is None:
            raise ConfigurationException('No configuration file was specified')

        # Confident we have custom, let's figure out the default.
        if self._default_config is None:
            # If the default config is not passed, we assume it's name and location
            # to be <base config file name>.default.ini
            self._default_config = os.path.splitext(self._custom_config)[0] + '.default.ini'

        # Now, we have both files, let's check to see if they exist.
        if not os.path.isfile(self._custom_config) \
                or not os.path.isfile(self._default_config):
            raise ConfigurationException(
                'One of custom ({0}) or default({1}) '
                'configuration files missing.'.format(self._custom_config, self._default_config))

        self._custom_config_parser = configparser.ConfigParser()
        self._custom_config_parser.read(self._custom_config)
        self._default_config_parser = configparser.ConfigParser()
        self._default_config_parser.read(self._default_config)

        # Now pull anything we need from the environment to update config.
        self._update_config_from_env()

        # Finally, cache the connection string for later.
        self._db_connection_string = self._rebuild_db_connection_string()

    @property
    def custom_config_file(self):
        """
        The custom configuration file path.
        
        :return: From where was the configuration read? (This is typically \
            a file path.
        :rtype: ``str``
        """
        return self._custom_config

    @property
    def default_config_file(self):
        """
        The default configuration file path.
        
        :return: The path to the default configuration file.
        :rtype: ``str``
        """
        return self._default_config

    def get(self, section, option, as_object=False, required=True):
        """
        Get a configuration option's value.

        :param section: the section in which the option is found
        :type section: ``str``
        :param option: the name of the option
        :type option: ``str``
        :param as_object: When ``True`` the method will attempt to convert the
            configuration option to a Python object.
        :type as_object: ``bool``
        :param required: When ``True`` the method returns ``None`` if no such
            configuration option exists.  Otherwise, an exception is thrown in
            this case.
        :type required: ``bool``
        :return: the configuration option value
        :rtype: ``str`` or ``object``
        :raise ConfigurationException: if the requested option is required but
            cannot be found
        """
        value = None

        try:
            opts_union = self.get_options(section)
            found = option in opts_union
        except ConfigurationException as ex:
            found = False

        if required and not found:
            raise ConfigurationException(
                'Option {0} not found not found..'.format(option))
        elif not required and not found:
            return None

        # If we're here, we know the value is there somewhere, so now try to find it.
        try:
            value = self._custom_config_parser.get(section, option)
        except(configparser.NoSectionError, configparser.NoOptionError) as ex:
            # Okay, wasn't in the custom, must be in the default.
            value = self._default_config_parser.get(section, option)

        # If the caller has asked to get the value as a Python object, evaluate
        # it now.
        if as_object:
            return eval(value)
        else:
            return value

    def get_options(self, section):
        """
        Get a list of all the options defined within a section.

        :param section: the section in whose options you want
        :type section: ``str``
        :return: a list of defined options
        :rtype: ``list`` of ``str``
        """
        try:
            cust_opts = self._custom_config_parser.options(section)
        except configparser.NoSectionError as noerr:
            # This is okay, we just need to look in the defaults.
            cust_opts = []

        try:
            default_opts = self._default_config_parser.options(section)
        except configparser.NoSectionError as noerr:
            # This could still be okay, depends on above.
            default_opts = []

        if not cust_opts and not default_opts:
            raise ConfigurationException(
                'Config section {0} not found.'.format(section))

        return list(set(cust_opts + default_opts))

    def get_sections(self):
        """
        Get a list of all the section names in this configuration object.
        
        :return: the defined section names
        :rtype: ``list``
        """
        return list(set(self._custom_config_parser.sections() + self._default_config_parser.sections()))
    
    def set_option(self, section, option, value):
        """
        Sets an option on a given section with the given value.  
        This value will not be persisted but will remain in effect as long
        as the application is running.  If the given section does not exist,
        it will be created.


        :param section: The section in which to put the option.
        :type section: ``str``
        :param option: The name of the option.
        :type option: ``str``
        :param value: The value to set for the option.
        :type value: ``str``
        """
        if section not in self.get_sections():
            self._custom_config_parser.add_section(section)
        
        self._custom_config_parser.set(section, option, value)

    def _update_config_from_env(self):
        """
        Does any work to pull configuration overrides from the environment.

        """
        # See if there is database information to be pulled from the
        # environment as well.
        env_dbhostname = os.getenv(_DBHOSTNAME)
        if env_dbhostname is not None:
            self.set_option('Database', 'host', env_dbhostname)

        env_dbport = os.getenv(_DBPORT)
        if env_dbport is not None:
            self.set_option('Database', 'port', env_dbport)

        env_dbname = os.getenv(_DBNAME)
        if env_dbname is not None:
            self.set_option('Database', 'dbname', env_dbname)

        env_username = os.getenv(_DBUSER)
        if env_username is not None:
            self.set_option('Database', 'username', env_username)

        env_password = os.getenv(_DBPASSWORD)
        if env_password is not None:
            self.set_option('Database', 'password', env_password)

        source_uri = os.getenv(_SOURCE_URI)
        if source_uri is not None:
            self.set_option('Service', 'source_uri', source_uri)

    def _rebuild_db_connection_string(self):
        """
        Recreates the database connection string from configuration.

        :return: ``str``
        """
        host = self.get('Database', 'host')
        port = self.get('Database', 'port')
        dbname = self.get('Database', 'dbname')
        user = self.get('Database', 'username')
        password = self.get('Database', 'password')

        # postgresql://scott:tiger@localhost/mydatabase'
        conn_string_template = 'postgresql://{0}:{1}@{2}:{3}/{4}'
        self._db_connection_string = conn_string_template.format(user, password, host, port, dbname)

    def get_db_connection_string(self):
        """
        Gets a valid database connection string from configuration.

        :rtype: ``str``
        """
        if self._db_connection_string is None:
            self._rebuild_db_connection_string()

        return self._db_connection_string





