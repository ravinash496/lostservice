#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: lostservice.defaultroutes.defaultroutehandler
.. moduleauthor:: Mike Anderson <manderson@geo-comm.com>

Classes to support Default Routes
"""
from lostservice.configuration import Configuration
from injector import inject
from lostservice.configuration import ConfigurationException
from lostservice.exception import NotFoundException
import uuid
import datetime
import abc
from abc import ABC
from enum import Enum
from lostservice.db.gisdb import GisDbInterface


class DefaultRouteModeEnum(Enum):
    OverrideRoute = "OverrideRoute"
    ExistingRoute = "ExistingRoute"
    CivicMatchingRule = "CivicMatchingRule"


class DefaultSetting(ABC):
    """
    An abstract class to wrap a default route setting retrieved from the configuration file (lostservice.ini)
    """
    def __init__(self, mode: str, urn: str):
        self.mode: DefaultRouteModeEnum = mode
        self.urn = urn

    @abc.abstractmethod
    def get_uri(self) -> str:
        """Get the uri """


class OverrideRouteSetting(DefaultSetting):
    """
    A class to wrap an override route default route setting from the config
    """
    def __init__(self, mode: str, urn: str, uri: str):
        super().__init__(mode, urn)
        self.uri = uri

    def get_uri(self):
        return self.uri


class ExistingRouteSetting(DefaultSetting):
    """
    a class to wrap an existing route default setting from the config
    """
    def __init__(self, mode: str, urn: str, boundary_id: str, db_wrapper: GisDbInterface):
        super().__init__(mode, urn)
        self.boundary_id = boundary_id
        self._db_wrapper = db_wrapper

    def get_uri(self):

        matching_boundary = self._db_wrapper.get_boundaries_for_previous_id(
            self.boundary_id,
            self._db_wrapper.get_urn_table_mappings()[self.urn])
        if not matching_boundary:
            return None
        else:
            return matching_boundary[0]['routeuri']



class DefaultRouteConfigWrapper(object):
    """
    A wrapper class for DefaultRouteHandler configuration related information.

    """
    @inject
    def __init__(self, config: Configuration, db_wrapper: GisDbInterface):
        """
        Constructor.

        :param config: The configuration object.
        :type config: :py:class:`lostservice.configuration.Configuration`
        """
        self._config = config
        self._db = db_wrapper

    def settings_for_default_route(self) -> [DefaultSetting] or None:
        """
        Get the default route settings
        :return:  default route settings
        """
        settings = self._config.get('Policy', 'default_routing_civic_policy', as_object=True, required=False)

        # it's ok not to have any settings
        if settings is None:
            return settings

        # if they have settings in lostservice.ini do some basic error checking
        # settings should be a dictionary with the first key == 'default_routes'
        # the value of settings['default_routes] should be a list of dictionaries
        # where each dictionary has three keys; 'OverrideRoute', 'urn' and 'uri'
        base_msg = "Error in lostservice.ini file. The default_routing_civic_policy setting is mis-configured"
        if 'default_routes' in settings:
            # first key is 'default_routes' , so far so good
            list_settings = settings['default_routes']
            if isinstance(list_settings, list):
                # the value of the first key is a list
                for setting in list_settings:
                    # check that this is a dictionary with three keys
                    if isinstance(setting, dict):
                        # it's a dictionary, now check that it has the right keys
                        if 'mode' not in setting:
                            # doesn't have the 'mode' key
                            err_msg = 'You must specify the mode for each item.'
                            raise ConfigurationException('{0} : {1}'.format(base_msg, err_msg))
                        else:
                            # it has the 'mode'
                            # check it it's set to a valid value
                            if setting['mode'] not in ['OverrideRoute', "ExistingRoute"]:
                                err_msg = 'Unsupported mode: {0}'.format(setting['mode'])
                                raise ConfigurationException('{0} : {1}'.format(base_msg, err_msg))
                        if 'urn' not in setting:
                            err_msg = 'You must specify the urn for each item.'
                            raise ConfigurationException('{0} : {1}'.format(base_msg, err_msg))
                        if setting['mode'] == 'OverrideRoute':
                            if 'uri' not in setting:
                                err_msg = 'You must specify the uri for each item that is in \
                                          OverrideRoute mode.'
                                raise ConfigurationException('{0} : {1}'.format(base_msg, err_msg))
                        elif setting['mode'] == 'ExistingRoute':
                            if 'boundaryid' not in setting:
                                err_msg = 'You must specify the boundaryid for each item that is in \
                                          ExistingRoute mode.'
                                raise ConfigurationException('{0} : {1}'.format(base_msg, err_msg))
                    else:
                        # the value of each the setting is not a dictionary, that's bad
                        err_msg = 'Each entry in the default_routes array must be an object.'
                        raise ConfigurationException('{0} : {1}'.format(base_msg, err_msg))
            else:
                err_msg = 'The first value must be an array of default route objects.'
                raise ConfigurationException('{0} : {1}'.format(base_msg, err_msg))
        else:
            err_msg = 'The first object name for the default_routing_civic_policy must be default_routes.'
            raise ConfigurationException('{0} : {1}'.format(base_msg, err_msg))

        if settings is None:
            return None
        else:
            default_routes = settings['default_routes']
            default_settings: [DefaultSetting] = []
            for setting in default_routes:
                if setting['mode'] == DefaultRouteModeEnum.OverrideRoute.value:
                    default_settings.append(OverrideRouteSetting(setting['mode'], setting['urn'],setting['uri']))
                elif setting['mode'] == DefaultRouteModeEnum.ExistingRoute.value:
                    default_settings.append(ExistingRouteSetting(setting['mode'],
                                                                 setting['urn'],
                                                                 setting['boundaryid'],
                                                                 self._db))
            return default_settings


class DefaultRouteHandler(object):
    """
        A class for handling default routes

        """
    @inject
    def __init__(self, config: DefaultRouteConfigWrapper):
        """
               Constructor

               :param config: The default route configuration wrapper object.
        """
        self._default_route_config = config

    def check_default_route(self, request):
        # Check for default routes
        # if there are none then throw a NotFoundException (return a notFound LoST error)
        default_route_uri = self._get_default_civic_route(request.service)
        if default_route_uri is None:
            raise NotFoundException('The server could not find an answer to the query.', None)
        else:
            # Create a default mapping given just a uri
            new_dict = {'serviceurn': request.service,
                        'routeuri': default_route_uri,
                        'displayname': '',
                        'srcunqid': str(uuid.uuid4()),
                        'servicenum': '',
                        'updatedate': str(datetime.datetime.utcnow()),
                        'default_route_used': True
                        }

            default_mapping = [new_dict]

            return default_mapping

    def _get_default_civic_route(self, service_urn: str) -> str or None:
        """
        Returns a uri if there is a match in the config file for the passed in urn
        :param service_urn:
        :return: uri or None
        """
        # get default route policies
        default_routes: [DefaultSetting] = self._default_route_config.settings_for_default_route()
        if default_routes is None:
            return None

        # get any matching configured urn's in the config, should only be 1 or 0
        matches: [DefaultSetting] = \
            [default_route for default_route in default_routes if default_route.urn == service_urn]
        if not matches:
            return None
        else:
            return matches[0].get_uri()
