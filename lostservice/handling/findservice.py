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
from lostservice.db.gisdb import GisDbInterface
from lxml import etree


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


class FindServiceException(Exception):
    """
    Raised when something goes wrong in the process of a findService request.

    :param message: The exception message
    :type message:  ``str``
    :param nested: Nested exception, if any.
    :type nested:
    """
    def __init__(self, message, nested=None):
        super().__init__(message)
        self._nested = nested


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
            buffer = 0.0

        return float(buffer)

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


class FindServiceImpl(object):
    """
    A class to handle the actual implementation of the various findService requests, responsible for making calls to
    the underlying database layers as well as applying policy.

    """
    def __init__(self, config: FindServiceConfigWrapper, db_wrapper: GisDbInterface):
        self._find_service_config = config
        self._db_wrapper = db_wrapper

    def _apply_point_multiple_match_policy(self, mappings):

        point_multiple_match_policy = self._find_service_config.get_point_multiple_match_policy()

        if point_multiple_match_policy is PointMultipleMatchPolicyEnum.ReturnAllLimit5:
            i = len(mappings)
            del mappings[5:i]  # removes items starting at 5 until the end of the list
        elif point_multiple_match_policy == PointMultipleMatchPolicyEnum.ReturnFirst:
            i = len(mappings)
            del mappings[1:i]  # removes items starting at 1 until the end of the list
        elif point_multiple_match_policy == PointMultipleMatchPolicyEnum.ReturnError.name:
            raise FindServiceException('Multiple results matched request location')

        return self._apply_service_boundary_policy(mappings)

    def _apply_polygon_multiple_match_policy(self, mappings):
        polygon_multiple_match_policy = self._find_service_config.get_polygon_multiple_match_policy()

        if polygon_multiple_match_policy == PolygonMultipleMatchPolicyEnum.ReturnAllLimit5:
            i = len(mappings)
            del mappings[5:i]  # removes items starting at 5 until the end of the list
        elif polygon_multiple_match_policy == PolygonMultipleMatchPolicyEnum.ReturnFirst:
            i = len(mappings)
            del mappings[1:i]  # removes items starting at 1 until the end of the list
        elif polygon_multiple_match_policy == PolygonMultipleMatchPolicyEnum.ReturnAreaMajority:
            # Find and return Max area
            max_area_item = max(mappings, key=lambda x: x['AREA_RET'])
            mappings = [max_area_item]
        elif polygon_multiple_match_policy == PolygonMultipleMatchPolicyEnum.ReturnError:
            raise FindServiceException('Multiple results matched request location')

        return self._apply_service_boundary_policy(mappings)

    def _apply_service_boundary_policy(self, results, request):

        # TODO -
        # Simplify - On
        # Simplify -Off
        # ReturnUnedited - Done
        # ReturnAreaMajorityPolygon
        # ReturnAllAsSinglePolygons

        if request.serviceBoundary == 'value':

            for row in results:
                if 'ST_AsGML_1' in row:
                    gml = row['ST_AsGML_1']
                    gml = gml.replace('>', ' xmlns:gml="http://www.opengis.net/gml">', 1)

                    root = etree.XML(gml)
                    root = self._clear_attributes(root)

                    # Update value with new GML
                    row['ST_AsGML_1'] = etree.tostring(root).decode("utf-8")

        return results

    def _clear_attributes(self, xml_element):
        """
        remove all attributes
        :param xml_element:
        :return:
        """
        for child in xml_element:
            child.attrib.clear()

            if len(xml_element):
                child = self._clear_attributes(child)

        return xml_element


class FindServiceWrapper(object):
    """
    A class to handle the tasks related to unwrapping findService requests and packaging up responses.

    """
    def __init__(self, impl: FindServiceImpl):
        self._impl = impl





