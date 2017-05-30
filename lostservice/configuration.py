#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: configuration
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

Configuration related classes and functions.
"""

import os
import configparser


# This is the default configuration.
_default = None


def set_config(configuration):
    """
    Set the default configuration object.

    :param configuration: the configuration object
    :type configuration: :py:class:`Configuration`
    """
    global _default
    _default = configuration


def get_config():
    """
    Get the configuration object.

    :return: the configuration object
    :rtype: :py:class:`Configuration`
    """
    global _default
    return _default


class ConfigurationException(Exception):
    """
    Something went wrong while loading, retrieving, or setting configuration
    values.
    """
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super(ConfigurationException, self).__init__(message)


class Configuration(object):
    """
    A wrapper for reading from and writing to a configuration file.

    """
    
    def __init__(self, custom_config, default_config=None):
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

        if self._default_config is None:
            # If the default config is not passed, we assume it's name and location
            # to be <base config file name>.default.ini
            self._default_config = os.path.splitext(self._custom_config)[0] + '.default.ini'

        if not os.path.isfile(self._custom_config) \
                or not os.path.isfile(self._custom_config):
            raise ConfigurationException(
                'One of custom ({0}) or default({1}) '
                'configuration files missing.'.format(self._custom_config, self._default_config))

        self._custom_config_parser = configparser.ConfigParser()
        self._custom_config_parser.read(self._custom_config)
        self._default_config_parser = configparser.ConfigParser()
        self._default_config_parser.read(self._default_config)

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




