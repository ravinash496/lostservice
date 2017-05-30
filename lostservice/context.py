#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: context
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

Provides functions and classes for contextual data required for processing.
"""

import lostservice.configuration as configuration
import os


_DBHOSTNAME = 'DBHOSTNAME'
_DBPORT = 'DBPORT'
_DBNAME = 'DBNAME'
_DBUSER = 'DBUSER'
_DBPASSWORD = 'DBPASSWORD'
_CONFIGFILE = 'CONFIGFILE'
_LOGFILE = 'LOGFILE'
_SOURCE_URI = 'SOURCE_URI'


class ContextException(Exception):
    """
    Something went wrong while setting up the context.
    """
    def __init__(self, message):
        """
        Constructor
        
        :param message: information about what went wrong.
        :type message: ``str``
        """
        # Call the base class constructor with the parameters it needs
        super(ContextException, self).__init__(message)


class LostContext(object):
    """
    A class which encapsulates all of the environmental
    information used during request processing.
    """
    def __init__(self, *args, **kwargs):
        """
        Constructor
        Will load configuration information in the following order:
        1) Look in the environment for a variable called CONFIGFILE and load 
           from there.
        2) Look for a parameter to the constructor called 'config_file' and 
           load that.
        3) Look for a parameter to the constructor called 'config_instance' 
           which is assumed to be an already hydrated instance of the 
           lostservice.configuration.Configuration class.

        :param config_file: The path to a config file - optional.
        :type config_file: ``str``
        :param config_instance: A Configuration object.
        :type config_instance: :py:class:`lostservice.configuration.Configuration`
        """
        super(LostContext, self).__init__()
        self._configuration = None
        self._config_file = None

        configfilename = os.getenv(_CONFIGFILE)
        if configfilename is not None:
            # Get the config file name from the environment.
            self._config_file = configfilename
            self._configuration = configuration.Configuration(configfilename)
        elif 'config_file' in kwargs.keys():
            # Config file name was passed in.
            self._config_file = kwargs.get('config_file')
            self._configuration = configuration.Configuration(self._config_file)
        elif 'config_instance' in kwargs.keys():
            # An instance of Configuration was passed in.
            self._configuration = kwargs.get('config_instance')
        else:
            raise ContextException(
                'No underlying configuration source was specified.')

        # Now pull anything we need from the environment to update config.
        self._update_config_from_env()

        # Finally, cache the connection string for later.
        self._db_connection_string = self._rebuild_db_connection_string()

    @property
    def configuration(self):
        """
        Property for accessing the underlying configuration object.
        :return: :py:class:`lostservice.configuration.Configuration`
        """
        return self._configuration

    def _update_config_from_env(self):
        """
        Does any work to pull configuration overrides from the environment.
         
        """
        # See if there is database information to be pulled from the
        # environment as well.
        env_dbhostname = os.getenv(_DBHOSTNAME)
        if env_dbhostname is not None:
            self._configuration.set_option('Database', 'host', env_dbhostname)

        env_dbport = os.getenv(_DBPORT)
        if env_dbport is not None:
            self._configuration.set_option('Database', 'port', env_dbport)

        env_dbname = os.getenv(_DBNAME)
        if env_dbname is not None:
            self._configuration.set_option('Database', 'dbname', env_dbname)

        env_username = os.getenv(_DBUSER)
        if env_username is not None:
            self._configuration.set_option('Database', 'username', env_username)

        env_password = os.getenv(_DBPASSWORD)
        if env_password is not None:
            self._configuration.set_option('Database', 'password', env_password)

        source_uri = os.getenv(_SOURCE_URI)
        if source_uri is not None:
            self.configuration.set_option('Service', 'source_uri', source_uri)

    def _rebuild_db_connection_string(self):
        """
        Recreates the database connection string from configuration.

        :return: ``str``
        """
        host = self._configuration.get('Database', 'host')
        port = self._configuration.get('Database', 'port')
        dbname = self._configuration.get('Database', 'dbname')
        user = self._configuration.get('Database', 'username')
        password = self._configuration.get('Database', 'password')

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




