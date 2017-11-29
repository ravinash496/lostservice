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
from lostservice.model.requests import FindServiceRequest
from typing import List
from lostservice.model.civic import CivicAddress

invalid_field_name = "invalid field name"


class DefaultRouteModeEnum(Enum):
    OverrideRoute = "OverrideRoute"
    ExistingRoute = "ExistingRoute"
    CivicMatchingRules = "CivicMatchingRules"


class CivicMatchingModeEnum(Enum):
    OverrideRoute = "OverrideRoute"
    ExistingRoute = "ExistingRoute"


class DefaultSetting(ABC):
    """
    An abstract class to wrap a default route setting retrieved from the configuration file (lostservice.ini)
    """
    def __init__(self, mode: str, urn: str):
        """

        :param mode: The mode for the default setting, should be a member of  DefaultRouteModeEnum
        :param urn: The service urn this policy applies to
        """
        self.mode: DefaultRouteModeEnum = mode
        self.urn = urn

    @abc.abstractmethod
    def get_uri(self, request: FindServiceRequest) -> str:
        """
        Get the uri
        :return: the uri
        """


class OverrideRouteSetting(DefaultSetting):
    """
    A class to wrap an override route default route setting from the config
    """

    def __init__(self, mode: str, urn: str, uri: str):
        """
        :param mode: The mode for the default setting, should be a member of  DefaultRouteModeEnum
        :param urn: The service urn this policy applies to
        :param uri: The uri to return for this policy
        """
        super().__init__(mode, urn)
        self.uri = uri

    def get_uri(self, request: FindServiceRequest):
        return self.uri


class ExistingRouteSetting(DefaultSetting):
    """
    a class to wrap an existing route default setting from the config
    """
    def __init__(self, mode: str, urn: str, boundary_id: str, db_wrapper: GisDbInterface):
        """

        :param mode: The mode for the default setting, should be a member of  DefaultRouteModeEnum
        :param urn:  The service urn this policy applies to
        :param boundary_id: The id to find matching row in esb... table matches srcunqid currently
        :param db_wrapper: the database wrapper to do the queries
        """
        super().__init__(mode, urn)
        self.boundary_id = boundary_id
        self._db_wrapper = db_wrapper

    def get_uri(self, request: FindServiceRequest):
        """
        Looks up  the uri in the database table using the boundaryid passed into the constructor
        :param request: not used for this implementation (overrides abstract method in base class)
        :return: None or the matching rows in the table
        """
        matching_boundary = self._db_wrapper.get_boundaries_for_previous_id(
            self.boundary_id,
            self._db_wrapper.get_urn_table_mappings()[self.urn])
        if not matching_boundary:
            return None
        else:
            return matching_boundary[0]['routeuri']


class CivicMatchingRule(ABC):
    """
    An abstract class to match civic matching rules from the default route configuration settings
    """
    def __init__(self, name: str, conditions: List[dict], mode: CivicMatchingModeEnum):
        self.name: str = name
        self.conditions: dict = conditions
        self.mode: CivicMatchingModeEnum = mode


class CivicOverrideMatchingRule(CivicMatchingRule):
    """
    Matching rule that uses OverrideRoute mode
    """
    def __init__(self, name: str, conditions: List[dict], mode: CivicMatchingModeEnum, uri: str):
        super().__init__(name, conditions, mode)
        self.uri = uri


class CivicExistingMatchingRule(CivicMatchingRule):
    """
    Matching rule that uses ExistingRoute mode
    """

    def __init__(self, name: str, conditions: List[dict], mode: CivicMatchingModeEnum, boundaryid: str):
        super().__init__(name, conditions, mode)
        self.boundaryid = boundaryid


class CivicMatchingSetting(DefaultSetting):
    """
    A class to wrap a CivicMatchingRules default setting from the config
    """

    def __init__(self, mode: str, urn: str, rules: List[dict],  db_wrapper: GisDbInterface):
        """

        :param mode: The mode for the default setting, should be a member of  DefaultRouteModeEnum
        :param urn:  The service urn this policy applies to
        :param rules: The civic matching rules
        :param db_wrapper: the database wrapper to do the queries
        """
        super().__init__(mode, urn)
        self.rules: [CivicMatchingRule] = self.build_rules(rules)
        self._db_wrapper = db_wrapper

    def get_uri(self, request: FindServiceRequest) -> str or None:
        """
        find an matching rule and return the uri
        :return:
        """
        # find matching rule
        for rule in self.rules:
                if isinstance(request.location.location, CivicAddress):
                    civic_address = request.location.location
                    if self.civic_location_matches_rule_conditions(civic_address, rule.conditions):
                        if isinstance(rule, CivicOverrideMatchingRule):
                            return rule.uri
                        elif isinstance(rule, CivicExistingMatchingRule):
                            matching_boundary = self._db_wrapper.get_boundaries_for_previous_id(
                                rule.boundaryid,
                                self._db_wrapper.get_urn_table_mappings()[self.urn])
                            if not matching_boundary:
                                return None
                            else:
                                return matching_boundary[0]['routeuri']

        return None

    def civic_location_matches_rule_conditions(self, civic_address: CivicAddress, conditions: dict) -> bool:
        """
        Return true if civic address matches all the conditions passed in
        :param civic_address:
        :param conditions:
        :return:
        """
        for key, value in conditions.items():
            if '_' + key.lower() in civic_address.keys():
                if value.lower() != civic_address['_' + key.lower()].lower():
                    return False
            else:
                return False
        return True

    @staticmethod
    def build_rules(rules: List[dict]) -> List[CivicMatchingRule]:
        """
        given some json build a list of rules
        :param rules: the json that represents the list of rules
        :return:
        """
        civic_matching_rules: [CivicMatchingRule] = []

        for rule in rules:
            if 'uri' in rule:
                civic_matching_rules.append(CivicOverrideMatchingRule(
                    rule['name'],
                    rule['conditions'],
                    CivicMatchingModeEnum.OverrideRoute,
                    rule['uri']))
            else:
                civic_matching_rules.append(CivicExistingMatchingRule(rule['name'],
                                                                      rule['conditions'],
                                                                      CivicMatchingModeEnum.OverrideRoute,
                                                                      rule['boundaryid']))
        return civic_matching_rules


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

    def settings_for_default_route(self, include_civic_defaults: bool = True) -> [DefaultSetting] or None:
        """
        Get the default route settings
        :param include_civic_defaults: include default settings targeted for civic requests
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
        if 'default_routes' in settings:
            # first key is 'default_routes' , so far so good
            list_settings = settings['default_routes']
            if isinstance(list_settings, list):
                # the value of the first key is a list
                for setting in list_settings:
                    # check that this is a dictionary with the right number of keys
                    if isinstance(setting, dict):
                        # it's a dictionary, now check that it has the right keys
                        if 'mode' not in setting:
                            # doesn't have the 'mode' key
                            self._error('You must specify the mode for each item.')
                        else:
                            # it has the 'mode'
                            # check it it's set to a valid value
                            if setting['mode'] not in DefaultRouteModeEnum.__members__:
                                self._error('Unsupported mode: {0}'.format(setting['mode']))
                        if 'urn' not in setting:
                            self._error('You must specify the urn for each item.')
                        if setting['mode'] == DefaultRouteModeEnum.OverrideRoute.value:
                            if 'uri' not in setting:
                                self._error('You must specify the uri for each item that is in '
                                            'OverrideRoute mode.')
                        elif setting['mode'] == DefaultRouteModeEnum.ExistingRoute.value:
                            if 'boundaryid' not in setting:
                                self._error('You must specify the boundaryid for each item that is in '
                                            'ExistingRoute mode.')
                        elif setting['mode'] == DefaultRouteModeEnum.CivicMatchingRules.value:
                            if 'rules' not in setting:
                                self._error('You must specify the rules for each item that is in '
                                            'CivicMatchingRules mode.')
                            elif self._check_rules(setting['rules']):
                                pass
                    else:
                        # the value of each the setting is not a dictionary, that's bad
                        self._error('Each entry in the default_routes array must be an object.')
            else:
                self._error('The first value must be an array of default route objects.')
        else:
            self._error('The first object name for the default_routing_civic_policy must be default_routes.')

        if settings is None:
            return None
        else:
            default_routes = settings['default_routes']
            default_settings: [DefaultSetting] = []
            for setting in default_routes:
                if setting['mode'] == DefaultRouteModeEnum.OverrideRoute.value:
                    default_settings.append(OverrideRouteSetting(setting['mode'], setting['urn'], setting['uri']))
                elif setting['mode'] == DefaultRouteModeEnum.ExistingRoute.value:
                    default_settings.append(ExistingRouteSetting(setting['mode'],
                                                                 setting['urn'],
                                                                 setting['boundaryid'],
                                                                 self._db))
                elif (setting['mode'] == DefaultRouteModeEnum.CivicMatchingRules.value and include_civic_defaults):
                    default_settings.append(CivicMatchingSetting(setting['mode'],
                                                                 setting['urn'],
                                                                 setting['rules'],
                                                                 self._db))
            return default_settings

    def _check_rules(self, rules) -> bool:
        """
        Basic checks for the rules element , returns true if valid, raises a configuration exception if not
        :param
        :param rules: a list of rules for a default routing civic policy
        :return: true if it passes basic checks for validity
        """
        if isinstance(rules, list):
            # rules are there check them
            # check that the value is a dict
            for rule in rules:
                if isinstance(rule, dict):
                    if 'name' not in rule:
                        self._error('Each rule must have a name element.')
                    if 'conditions' not in rule:
                        self._error('Each rule must have a conditions element.')
                    if 'mode' not in rule:
                        self._error('Each rule must have a mode element.')
                    else:
                        if rule['mode'] not in CivicMatchingModeEnum.__members__:
                            self._error('Only modes of "OverrideRoute" or "ExistingRoute"' 
                                        'are supported for civic address rule types.')
                        else:
                            if rule['mode'] == CivicMatchingModeEnum.OverrideRoute.value and 'uri' not in rule:
                                self._error('Each rule where mode is OverrideRoute must have a uri element.')
                            if rule['mode'] == CivicMatchingModeEnum.ExistingRoute.value and 'boundaryid' not in rule:
                                self._error('Each rule where mode is ExistingRoute must have a boundaryid element.')
                else:
                    self._error('Each rule in rules must be a dictionary of key value pairs.')
        else:
            self._error('The rules element value must be an array of rules.')

        # if it makes it here it passed all the tests.
        return True

    @staticmethod
    def _error(err_msg):
        """
        Raise a ConfigurationException
        :param err_msg: the rest of the error message
        :return: None
        """
        base_msg = "Error in lostservice.ini file. The default_routing_civic_policy setting is mis-configured"
        raise ConfigurationException('{0} : {1}'.format(base_msg, err_msg))


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
        default_route_uri = None
        if type(request.location.location) is CivicAddress:
            default_route_uri = self._get_default_civic_route(request)
        else:
            default_route_uri = self._get_default_route(request)

        if default_route_uri is None:
            raise NotFoundException('The server could not find an answer to the query.')
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

    def _get_default_civic_route(self, request: FindServiceRequest) -> str or None:
        """
        Returns a uri if there is a match in the config file for the passed in urn
        :param request: The request object
        :return: uri or None
        """
        # get default route policies
        default_routes: [DefaultSetting] = self._default_route_config.settings_for_default_route()
        if default_routes is None:
            return None

        # get any matching configured urn's in the config, should only be 1 or 0
        matches: [DefaultSetting] = \
            [default_route for default_route in default_routes if default_route.urn == request.service]
        if not matches:
            return None
        else:
            return matches[0].get_uri(request)

    def _get_default_route(self, request: FindServiceRequest) -> str or None:
        """
        Returns a uri if there is a match in the config file for the passed in urn
        :param request: The request object
        :return: uri or None
        """
        # get default route policies
        default_routes: [DefaultSetting] = self._default_route_config.settings_for_default_route(
            include_civic_defaults=False)
        if default_routes is None:
            return None

        # get any matching configured urn's in the config, should only be 1 or 0
        matches: [DefaultSetting] = \
            [default_route for default_route in default_routes if default_route.urn == request.service]
        if not matches:
            return None
        else:
            return matches[0].get_uri(request)
