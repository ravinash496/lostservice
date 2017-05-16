#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: configuration
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

Configuration related classes and functions.
"""

import configparser

# This is the ID that identifies the default configuration.
DEFAULT = "default"

# This is the default configuration.
_default = None


def set(configuration):
    """
    Set the default configuration object.

    :param configuration: the configuration object
    :type configuration: :py:class:`Configuration`
    """
    global _default
    _default = configuration


def get():
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
    
    def __init__(self, file):
        """
        Constructor

        :param file: The full path to the configuration (.ini) file.
        :type str: ``str``
        """
        super(Configuration, self).__init__()
        self._file = file
        self._config_parser = configparser.ConfigParser()
        self._config_parser.read(file)

    @property
    def file(self):
        """
        The configuration file path.
        
        :return: From where was the configuration read? (This is typically \
            a file path.
        :rtype: ``str``
        """
        return self._file

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
        # For starters, let's just try to get the value.
        try:
            value = self._config_parser.get(section, option)
        except configparser.NoOptionError as noerr:
            # A NoOptionError means the option doesn't exist.
            if not required:
                return None
            else:
                raise ConfigurationException(
                    'Missing configuration option: "{0}|{1}"'.format(section,
                                                                     option))
        except configparser.NoSectionError as ex:
            if not required:
                return None
            else:
                raise ConfigurationException(
                    ('Could not read configuration option: "{0}|{1}" ' + \
                     'because the "{0}" section is missing.').format(section, 
                                                                     option))
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
        return self._config_parser.options(section)

    def get_sections(self):
        """
        Get a list of all the section names in this configuration object.
        
        :return: the defined section names
        :rtype: ``list``
        """
        return self._config_parser.sections()



