#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. currentmodule:: lostservice.handling.findservice
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

Implementation classes for findservice queries.
"""

from enum import Enum
from injector import inject
from lostservice.configuration import Configuration


class ServiceExpiresPolicyEnum(Enum):
    NoCache = 1
    NoExpiration = 2
    TimeSpan = 3


class PolygonSearchModePolicyEnum(Enum):
    SearchUsingPolygon = 1
    SearchUsingCentroid = 2


class PolygonMultipleMatchPolicyEnum(Enum):
    ReturnAll = 1
    ReturnAllLimit5 = 2
    ReturnAreaMajority = 3
    ReturnFirst = 4
    ReturnError = 5


class PointMultipleMatchPolicyEnum(Enum):
    ReturnAll = 1
    ReturnAllLimit5 = 2
    ReturnFirst = 3
    ReturnError = 4


class FindServiceConfigWrapper(object):
    """
    A wrapper class for findservice configuration related information.

    """
    @inject
    def __init__(self, config: Configuration):
        """
        Constructor.

        :param config: a reference to the configuration object.
        """
        self._config = config

    def get_proximity_search_policy(self):
        """
        Gets the proximity search policy.

        :return: ``bool``
        """
        policy = self._config.get('Policy', 'service_boundary_proximity_search_policy', as_object=True, required=False)
        if policy is None:
            policy = False
        return policy

    def get_service_boundary_proximity_buffer(self):
        """
        Gets the service boundary proximity buffer.

        :return: ``int``
        """
        buffer = self._config.get('Policy', 'service_boundary_proximity_buffer', as_object=False, required=False)
        if buffer is None:
            buffer = 0

        return buffer

    def get_polygon_multiple_match_policy(self):
        """
        Gets the polygon multiple match policy.

        :return: :py:class:`PolygonMultipleMatchPolicyEnum`
        """
        retval = None
        policy = self._config.get('Policy', 'polygon_multiple_match_policy', as_object=False, required=False)
        if policy is not None:
            try:
                retval = PolygonMultipleMatchPolicyEnum[policy]
            except KeyError:
                retval = None

        return retval

    def get_polygon_search_mode_policy(self):
        """
        Gets the polygon search mode policy.

        :return: :py:class:`PolygonSearchModePolicyEnum`
        """
        retval = None
        policy = self._config.get('Policy', 'polygon_search_mode_policy', as_object=False, required=False)
        if policy is not None:
            try:
                retval = PolygonSearchModePolicyEnum[policy]
            except KeyError:
                retval = None

        return retval

    def get_point_multiple_match_policy(self):
        """
        Gets the point search mode policy.

        :return: :py:class:`PointMultipleMatchPolicyEnum`
        """
        retval = None
        policy = self._config.get('Policy', 'point_multiple_match_policy', as_object=False, required=False)
        if policy is not None:
            try:
                retval = PointMultipleMatchPolicyEnum[policy]
            except KeyError:
                retval = None

        return retval




