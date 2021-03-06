#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. currentmodule:: lostservice.handling.findservice
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

Implementation classes for findservice queries.
"""

import datetime
import pytz
from enum import Enum
from injector import inject
from lostservice.configuration import Configuration
from lostservice.exception import InternalErrorException
from lostservice.model.responses import FindServiceResponse, ResponseMapping, AdditionalDataResponseMapping
from lostservice.exception import ServiceNotImplementedException, LoopException, NotFoundException
import lostservice.geometry as geom
from lostservice.geometryutility import GeometryUtility
from lostservice.db.gisdb import GisDbInterface
from lxml import etree
from shapely.geometry import Polygon
import json
from lostservice.configuration import general_logger
from civvy.db.postgis.query import PgQueryExecutor
from civvy.db.postgis.locating.streets import PgStreetsAggregateLocatorStrategy
from civvy.db.postgis.locating.points import PgPointsAggregateLocatorStrategy
from civvy.locating import CivicAddress, CivicAddressSourceMapCollection, Locator

logger = general_logger()
from lostservice.model.geodetic import Point
from lostservice.model.geodetic import Polygon as geodetic_polygon


class ServiceExpiresPolicyEnum(Enum):
    NoCache = 1
    NoExpiration = 2
    TimeSpan = 3


class PolygonSearchModePolicyEnum(Enum):
    SearchUsingPolygon = 1
    SearchUsingCentroid = 2


class PolygonMultipleMatchPolicyEnum(Enum):
    ReturnFirst = 1
    ReturnAreaMajority = 2
    ReturnLimitWarning = 3


class PointMultipleMatchPolicyEnum(Enum):
    ReturnFirst = 1
    ReturnLimitWarning = 2
    ReturnError = 3


class ServiceBoundaryGeodeticOverridePolicyEnum(Enum):
    MatchRequest = 1
    ReturnReference = 2
    ReturnValue = 3
    ReturnNothing = 4


class ServiceBoundaryCivicOverridePolicyEnum(Enum):
    MatchRequest = 1
    # TODO


class FindServiceConfigWrapper(object):
    """
    A wrapper class for findservice configuration related information.

    """
    @inject
    def __init__(self, config: Configuration):
        """
        Constructor.

        :param config: The configuration object.
        :type config: :py:class:`lostservice.configuration.Configuration`
        """
        self._config = config

    def do_expanded_search(self):
        """
        Gets the proximity search policy.

        :return: ``bool``
        """
        policy = self._config.get('Policy', 'service_boundary_proximity_search_policy', as_object=True, required=False)
        if policy is None:
            policy = False
        return policy

    def expanded_search_buffer(self):
        """
        Gets the service boundary proximity buffer.

        :return: ``float``
        """
        buffer = self._config.get('Policy', 'service_boundary_proximity_buffer', as_object=False, required=False)
        if buffer is None:
            buffer = 0.0

        return float(buffer)

    def polygon_multiple_match_policy(self):
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

    def polygon_result_limit_policy(self):
        """
        Gets the maximum number mappings to return. If results exceeds this value include a "toomanyMappings" warning.

        :return: ``int``
        """
        limit = self._config.get('Policy', 'polygon_return_limit_number', as_object=False, required=False)
        if limit is None:
            limit = 5  # Default to 5

        return int(limit)

    def additionaldata_result_limit(self):
        """
        Gets the maximum number mappings to return. If results exceeds this value include a "toomanyMappings" warning.

        :return: ``int``
        """
        limit = self._config.get('AddtionalData', 'return_limit_number', as_object=False, required=False)
        if limit is None:
            limit = 100  # Default to 100

        return int(limit)

    def polygon_search_mode_policy(self):
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

    def point_multiple_match_policy(self):
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

    def point_result_limit_policy(self):
        """
        Gets the maximum number mappings to return. If results exceeds this value include a "toomanyMappings" warning.

        :return: ``int``
        """
        limit = self._config.get('Policy', 'point_return_limit_number', as_object=False, required=False)
        if limit is None:
            limit = 5  # Default to 5

        return int(limit)

    def source_uri(self) -> str:
        """
        Gets the source URI.

        :return: The configured source URI.
        :rtype: ``str``
        """
        uri = self._config.get('Service', 'source_uri', as_object=False, required=False)
        if uri is None:
            uri = ''
        return uri

    def settings_for_service(self, service):
        """
        Get the service settings for the given boundary.

        :param service: The name of the service boundary.
        :type service: ``str``
        :return: ``dict``
        """
        settings = self._config.get('Service', service, as_object=True, required=False)
        if settings is None:
            # Config not set for specific table use default Service Values
            settings = self._config.get('Service', 'default', as_object=True, required=False)
        return settings

    def settings_for_additionaldata(self, param):
        """
        Get the addtional data settings.
        :param param: name of the parameter to get the setting
        :type param: ``str``
        :return: ``str``
        """
        settings = self._config.get('AddtionalData', param, as_object=False, required=False)
        if settings is None:
            return ""
        return settings

    def additional_data_uri(self) -> str:
        """
        Gets the additional data URI.

        :return: The configured additional data URI.
        :rtype: ``str``
        """
        uri = self._config.get('AddtionalData', 'service_urn', as_object=False, required=False)
        if uri is None:
            uri = ''
        return uri

    def additional_data_buffer(self) -> float:
        """
        Gets the additional data buffer.

        :return: The configured additional data buffer.
        :rtype: ``float``
        """
        buffer = self._config.get('AddtionalData', 'buffer_meters', as_object=False, required=False)
        if buffer is None:
            buffer = 0.0
        return float(buffer)

    def service_boundary_return_geodetic_override(self):
        """
        Gets the Geodetic service boundary override mode policy.

        :return: :py:class:`ServiceBoundaryGeodeticOverridePolicyEnum`
        """
        retval = None
        policy = self._config.get('Policy', 'service_boundary_return_geodetic_override',
                                  as_object=False, required=False)
        if policy is not None:
            try:
                retval = ServiceBoundaryGeodeticOverridePolicyEnum[policy]
            except KeyError:
                retval = None

        return retval

    def service_boundary_return_civic_override(self):
        """
        Gets the Civic service boundary override mode policy.

        :return: :py:class:`ServiceBoundaryCivicOverridePolicyEnum`
        """
        retval = None
        policy = self._config.get('Policy', 'service_boundary_return_civic_override', as_object=False,
                                  required=False)
        if policy is not None:
            try:
                retval = ServiceBoundaryCivicOverridePolicyEnum[policy]
            except KeyError:
                retval = None

        return retval

    def do_polygon_simplification(self) -> bool:
        """
        Gets the polygon simplification policy.

        :return: ``bool``
        """
        policy = self._config.get('Policy', 'service_boundary_simplify_result', as_object=True, required=False)
        if policy is None:
            policy = False
        return policy

    def simplification_tolerance(self) -> float:
        """
        Gets the tolerance range for simplification.

        :return: ``float``
        """
        tolerance = self._config.get('Policy', 'service_boundary_simplify_tolerance', as_object=False, required=False)
        if tolerance is None:
            tolerance = 0.0

        return float(tolerance)

    def use_fuzzy_match(self) -> bool:
        """
        Gets value to see if we should use fuzzy results or not.

        :return:  `` bool``
        """
        fuzzy = self._config.get('Service', 'use_fuzzy_match', as_object=True, required=False)
        if fuzzy is None:
            fuzzy = True
        return fuzzy

    def find_civic_address_maximum_score(self) -> float:
        """
        Gets the maximum score before find service returns notFound error.

        :return: ``float``
        """
        maximum = self._config.get('Service', 'find_civic_address_maximum_score', as_object=False, required=False)
        if maximum is None:
            maximum = .05

        return float(maximum)

    def offset_distance(self) -> int:
        """
        Gets the offset distance to set road centerline points from the center... line.
        :return:  ``int``
        """
        offset = self._config.get('Policy', 'offset_distance_from_centerline', as_object=False, required=False)
        if offset is None:
            offset = 10
        return offset


class FindServiceInner(object):
    """
    A class to handle the actual implementation of the various findService requests, responsible for making calls to
    the underlying database layers as well as applying policy.

    """
    @inject
    def __init__(self,
                 config: FindServiceConfigWrapper,
                 db_wrapper: GisDbInterface,
                 query_executor: PgQueryExecutor=None):
        """
        Constructor

        :param config: The FindService configuration wrapper object.
        :type config: :py:class:`lostservice.handling.FindServiceConfigWrapper`
        :param db_wrapper: The db wrapper class instance.
        :type db_wrapper: :py:class:`lostservice.db.gisdb.GisDbInterface`
        :param query_executor: A query executor with pooled connections.
        :type query_executor: :py:class:civvy.db.postgis.query.PgQueryExecutor`
        """
        # TODO: There shouldn't be a default for query_executor,
        # this was to facilitate not breaking existing unit tests for now.
        self._find_service_config = config
        self._db_wrapper = db_wrapper
        self._mappings = self._db_wrapper.get_urn_table_mappings()
        self._geomutil = GeometryUtility()
        self._query_executor = query_executor
        self._fuzzy_used = False

    @property
    def fuzzy_used(self):
        """
        If we used the fuzzy match scoring principle or not when choosing a point for find service.

        :return: ``str``
        """
        return self._fuzzy_used

    def _get_esb_table(self, service_urn):
        """
        Get the service boundary table for the given URN.

        :param service_urn: The service URN.
        :type service_urn: ``str``
        :return: The table name.
        :rtype: ``str``
        """
        if service_urn in self._mappings:
            return self._mappings[service_urn]
        else:
            logger.warning('Service URN {0} not supported.'.format(service_urn))
            raise ServiceNotImplementedException('Service URN {0} not supported.'.format(service_urn), None)

    def find_service_for_point(self, service_urn, geodetic_location, return_shape=False):
        """
        Find services for the given point.

        :param service_urn: The identifier for the service to look up.
        :type service_urn: ``str``
        :param geodetic_location: location object.
        :type geodetic_location: `location object`
        :param return_shape: Whether or not to return the geometries of found mappings.
        :type return_shape: ``bool``
        :return: The service mappings for the given point.
        :rtype: ``list`` of ``dict``
        """
        ADD_DATA_REQUESTED = False
        ADD_DATA_SERVICE = self._find_service_config.additional_data_uri()
        buffer_distance = self._find_service_config.additional_data_buffer()
        if service_urn.lower() == ADD_DATA_SERVICE.lower():
            ADD_DATA_REQUESTED = True
            esb_table = self._find_service_config.settings_for_additionaldata("data_table")
        else:
            esb_table = self._get_esb_table(service_urn)

        results = self._db_wrapper.get_containing_boundary_for_point(
            geodetic_location,
            esb_table,
            add_data_requested=ADD_DATA_REQUESTED,
            buffer_distance=buffer_distance)

        if not ADD_DATA_REQUESTED:
            if results is not None and len(results) != 0:
                results = self._apply_point_multiple_match_policy(results)
            elif self._find_service_config.do_expanded_search():

                multiple_match_policy = self._find_service_config.polygon_multiple_match_policy()
                return_area = multiple_match_policy is PolygonMultipleMatchPolicyEnum.ReturnAreaMajority
                proximity_buffer = self._find_service_config.expanded_search_buffer()

                # TODO, what is our UOM for buffers, assert meters?
                results = self._db_wrapper.get_intersecting_boundaries_for_circle(
                    location=geodetic_location,
                    boundary_table=esb_table,
                    return_area=return_area,
                    return_shape=return_shape,
                    proximity_search=True,
                    proximity_buffer=proximity_buffer)

                results = self._apply_polygon_multiple_match_policy(results)
        else:
            if results is None:
                results = [{'adddatauri': ""}]

        return self._apply_policies(results, return_shape)

    def get_civvy_locator(self, offset_distance):
        """
        Creates the locator(s) needed for civic address location searching.
        :param offset_distance: distance to offset RCL point matches
        :type civic_request: int
        :return: a collection of civic address locator(s)
        :rtype:
        """
        # The locator needs some information about the underlying data store.
        civvy_json = json.dumps(self._find_service_config.settings_for_service("civvy_map"))

        # From the JSON configuration, create the source maps that apply to this database.
        source_maps = CivicAddressSourceMapCollection(config=civvy_json)


        # Now let's create the locator and supply it with the common default strategies.
        locator = Locator(strategies=[
            PgPointsAggregateLocatorStrategy(query_executor=self._query_executor),
            PgStreetsAggregateLocatorStrategy(query_executor=self._query_executor)
        ], source_maps=source_maps, offset_distance=offset_distance)

        return locator

    def run_civic_location_search(self, locator, offset_distance, civic_request):
        """
        Creates a dictionary of values to pass into the civvy library to run civic address match queries.
        :param locator:
        :param offset_distance: the distance to offset the resultant point of an RCL match.
        :param civic_request: int
        :return: a collection of results from the civic location queries.
        """

        # Make sure we have a locator to use first.
        if locator is not None:
            civvy_obj = civic_request.location.location
            # Create dictionary of values from request into a civic location dictionary for civvy to use.
            civic_dict = {}
            civic_dict['country'] = civvy_obj.country
            if civvy_obj.a1:
                civic_dict['a1'] = civvy_obj.a1
            if civvy_obj.a2:
                civic_dict['a2'] = civvy_obj.a2
            if civvy_obj.a3:
                civic_dict['a3'] = civvy_obj.a3
            if civvy_obj.a4:
                civic_dict['a4'] = civvy_obj.a4
            if civvy_obj.a5:
                civic_dict['a5'] = civvy_obj.a5
            if civvy_obj.a6:
                civic_dict['a6'] = civvy_obj.a6
            if civvy_obj.rd:
                civic_dict['rd'] = civvy_obj.rd
            if civvy_obj.pod:
                civic_dict['pod'] = civvy_obj.pod
            if civvy_obj.sts:
                civic_dict['sts'] = civvy_obj.sts
            if civvy_obj.hno:
                civic_dict['hno'] = civvy_obj.hno
            if civvy_obj.hns:
                civic_dict['hns'] = civvy_obj.hns
            if civvy_obj.lmk:
                civic_dict['lmk'] = civvy_obj.lmk
            if civvy_obj.loc:
                civic_dict['loc'] = civvy_obj.loc
            if civvy_obj.flr:
                civic_dict['flr'] = civvy_obj.flr
            if civvy_obj.nam:
                civic_dict['nam'] = civvy_obj.nam
            if civvy_obj.pc:
                civic_dict['pc'] = civvy_obj.pc
            if civvy_obj.pom:
                civic_dict['pom'] = civvy_obj.pom
            if civvy_obj.hnp:
                civic_dict['hnp'] = civvy_obj.hnp
            if civvy_obj.lmkp:
                civic_dict['lmkp'] = civvy_obj.lmkp
            if civvy_obj.mp:
                civic_dict['mp'] = civvy_obj.mp

            # We can create several civic addresses and pass them to the locator.
            civic_address = CivicAddress(**civic_dict)
            logger.info('Executing civic address query')
            # Let's get the results for this civic address.
            logger.debug('Running civic address query for find service through civvy.')
            locator_results = locator.locate_civic_address(civic_address=civic_address, offset_distance=offset_distance)

            return locator_results
        else:
            # Who did this, and why are you doing it?!
            logger.error('Locator object not passed.')
            raise NotFoundException('Locator not defined, cannot complete civic address request.', None)
            return None

    def find_service_for_civicaddress(self, civic_request: CivicAddress, return_shape: bool=False):
        """
         Function to find the service for the civic address
         :param civic_request: civic address request
         :type civic_request: :py:class:`lostservice.model.requests.FindServiceRequest`
         :param return_shape: Whether or not to return the geometries of found mappings.
         :type return_shape: bool
         :return: The service mappings for the given civic address.
         """
        # Get the RCL offset distance from configuration
        rcl_offset_distance = self._find_service_config.offset_distance()
        # Create the locator we want to use for civic address location searching. (Can be multiple locators)
        locator = self.get_civvy_locator(rcl_offset_distance)
        # Run our civic address location search.
        locator_results = self.run_civic_location_search(locator=locator,
                                                         offset_distance=rcl_offset_distance,
                                                         civic_request=civic_request)

        if locator_results is not None and len(locator_results) > 0:
            use_fuzzy = self._find_service_config.use_fuzzy_match()  # Do we use fuzzy matching or not.
            max_score = self._find_service_config.find_civic_address_maximum_score()
            civic_point = locator_results[0]  # We will always use the first result from civvy for our find service.
            # We want an exact match from our civic address query
            # or if fuzzy matching is on, we are within the score tolerance.
            if civic_point.score == 0.0 or (civic_point.score <= max_score and use_fuzzy):
                logger.info(f'Point found and used for civic address request. Score: {civic_point.score}')
                spatial_reference = civic_point.geometry.GetSpatialReference()
                epsg = spatial_reference.GetAttrValue("AUTHORITY", 0)
                srid = spatial_reference.GetAttrValue("AUTHORITY", 1)
                spatial_ref = "{0}::{1}".format(epsg, srid)
                point = Point()
                point.latitude = civic_point.geometry.GetY()
                point.longitude = civic_point.geometry.GetX()
                point.spatial_ref = spatial_ref
                mappings = self.find_service_for_point(civic_request.service,
                                                       point,
                                                       return_shape=return_shape)
                # Add location validation results to response as needed.
                validate_location = False
                if hasattr(civic_request, 'validateLocation'):
                    validate_location = civic_request.validateLocation

                if validate_location:
                    logger.info('Validating Location. . .')
                    location_validation = {}
                    # valid properties
                    valid_properties = [prop.value for prop in civic_point.valid_civic_address_properties]
                    if len(valid_properties) > 0:
                        location_validation['valid'] = " ".join(valid_properties)
                    # invalid properties
                    invalid_properties = [prop.value for prop in civic_point.invalid_civic_address_properties]
                    if len(invalid_properties) > 0:
                        location_validation['invalid'] = " ".join(invalid_properties)
                    # unchecked properties
                    unchecked_properties = [prop.value for prop in civic_point.unchecked_civic_address_properties]
                    if len(unchecked_properties) > 0:
                        location_validation['unchecked'] = " ".join(unchecked_properties)
                    mappings[0]['locationValidation'] = location_validation

                # If we used a fuzzy match, we want to build a warning for it later.
                if civic_point.score != 0.0 and (civic_point.score <= max_score and use_fuzzy):
                    self._fuzzy_used = True
                    logger.info(f'Fuzzy matching used for response. Score: {civic_point.score}')

                return {'mappings': mappings,
                        'latitude': point.latitude,
                        'longitude': point.longitude}
            else:
                # our first result score is too high, send a not found exception.
                raise NotFoundException('The server could not find an answer to the query.', None)
        else:
            # We couldn't find anything, so return nothing.
            raise NotFoundException('The server could not find an answer to the query.', None)
        # Nothing good came of this.
        logger.info('No valid mappings found.')
        return None

    def find_service_for_circle(self,
                                service_urn,
                                location,
                                return_shape=False):
        """
        Find services for the given circle.

        :param service_urn: The identifier for the service to look up.
        :type service_urn: ``str``
        :param location: Geodetic location object .
        :type location: ``location object``
        :param return_shape: Whether or not to return the geometries of found mappings.
        :type return_shape: ``bool``
        :return: The service mappings for the given circle.
        :rtype: ``list`` of ``dict``
        """

        if self._find_service_config.polygon_search_mode_policy() is PolygonSearchModePolicyEnum.SearchUsingCentroid:
            # search using a centroid.
            location_point = Point()
            location_point.longitude = location.longitude
            location_point.latitude = location.latitude
            location_point.spatial_ref = location.spatial_ref
            return self.find_service_for_point(service_urn, location_point, return_shape)
        else:
            ADD_DATA_REQUESTED = False
            ADD_DATA_SERVICE = self._find_service_config.additional_data_uri()
            buffer_distance = self._find_service_config.additional_data_buffer()
            if service_urn == ADD_DATA_SERVICE:
                ADD_DATA_REQUESTED = True
                esb_table = self._find_service_config.settings_for_additionaldata("data_table")
            else:
                esb_table = self._get_esb_table(service_urn)

            multiple_match_policy = self._find_service_config.polygon_multiple_match_policy()
            return_area = multiple_match_policy is PolygonMultipleMatchPolicyEnum.ReturnAreaMajority

            if ADD_DATA_REQUESTED:
                results = self._db_wrapper.get_additional_data_for_circle(
                    location,
                    esb_table,
                    buffer_distance)
                results = self._apply_addtionaldata_multiple_match_policy(results)
                if results is None or len(results)==0:
                    results = [{'adddatauri':''}]
            else:
                results = self._db_wrapper.get_intersecting_boundaries_for_circle(
                    location, esb_table, return_area, return_shape)

                if (results is None or len(results) == 0) and self._find_service_config.do_expanded_search():
                    proximity_buffer = self._find_service_config.expanded_search_buffer()
                    results = self._db_wrapper.get_intersecting_boundaries_for_circle(
                        location,
                        esb_table,
                        return_area,
                        return_shape,
                        True,
                        proximity_buffer)

                results = self._apply_polygon_multiple_match_policy(results)
            return self._apply_policies(results, return_shape)

    def find_service_for_ellipse(self,
                                 service_urn,
                                 location,
                                 return_shape=False):
        """
        Find services for the given ellipse.

        :param service_urn: The identifier for the service to look up.
        :type service_urn: ``str``
        :param location: Geodetic location object .
        :type location: ``location object``
        :param return_shape: Whether or not to return the geometries of found mappings.
        :type return_shape: ``bool``
        :return: The service mappings for the given ellipse.
        :rtype: ``list`` of ``dict``
        """
        # TODO: does there need to be an orientation UOM?
        # TODO: Why do the ellipse queries always return the intersection areas but others don't?

        if self._find_service_config.polygon_search_mode_policy() is PolygonSearchModePolicyEnum.SearchUsingCentroid:
            # search using a centroid.
            point = Point()
            point.longitude = location.longitude
            point.latitude = location.latitude
            point.spatial_ref = location.spatial_ref
            return self.find_service_for_point(service_urn, point, return_shape)
        else:
            ADD_DATA_REQUESTED = False
            ADD_DATA_SERVICE = self._find_service_config.additional_data_uri()
            buffer_distance = self._find_service_config.additional_data_buffer()
            if service_urn == ADD_DATA_SERVICE:
                ADD_DATA_REQUESTED = True
                esb_table = self._find_service_config.settings_for_additionaldata("data_table")
            else:
                esb_table = self._get_esb_table(service_urn)

            if ADD_DATA_REQUESTED:
                results = self._db_wrapper.get_additional_data_for_ellipse(
                    location,
                    esb_table,
                    buffer_distance)
                results = self._apply_addtionaldata_multiple_match_policy(results)
                if results is None or len(results) == 0:
                    results = [{'adddatauri': ''}]
            else:
                results = self._db_wrapper.get_intersecting_boundary_for_ellipse(
                    location,
                    esb_table)

                if (results is None or len(results) == 0) and self._find_service_config.do_expanded_search():
                    # No results and Policy says we should buffer and research
                    proximity_buffer = self._find_service_config.expanded_search_buffer()
                    location.majorAxis = location.majorAxis+proximity_buffer
                    location.minorAxis = location.minorAxis+proximity_buffer
                    results = self._db_wrapper.get_intersecting_boundary_for_ellipse(
                        location,
                        esb_table)

                results = self._apply_polygon_multiple_match_policy(results)
            return self._apply_policies(results, return_shape)

    def find_service_for_arcband(self,
                                 service_urn,
                                 location,
                                 return_shape=False):
        """
        Find services for the given arcband.

        :param service_urn: The identifier for the service to look up.
        :type service_urn: ``str``
        :param location: Geodetic location object .
        :type location: ``location object``
        :param return_shape: Whether or not to return the geometries of found mappings.
        :type return_shape: ``bool``
        :return: The service mappings for the given arcband.
        :rtype: ``list`` of ``dict``
        """

        WGS84SPATIALREFERENCE = 'urn:ogc:def:crs:EPSG::4326'

        arcband = geom.generate_arcband(location.longitude,
                                        location.latitude,
                                        location.spatial_ref,
                                        location.start_angle,
                                        location.opening_angle,
                                        location.inner_radius,
                                        location.outer_radius)
        points = geom.get_vertices_for_geom(arcband)[0]
        polygon = geodetic_polygon()
        polygon.spatial_ref = WGS84SPATIALREFERENCE
        polygon.vertices = points
        return self.find_service_for_polygon(service_urn, polygon, return_shape)

    def find_service_for_polygon(self, service_urn, location, return_shape=False):
        """
        Find services for the given polygon.

        :param service_urn: The identifier for the service to look up.
        :type service_urn: ``str``
        :param location: Geodetic location object .
        :type location: ``location object``
        :param return_shape: Whether or not to return the geometries of found mappings.
        :type return_shape: ``bool``
        :return: The service mappings for the given polygon.
        :rtype: ``list`` of ``dict``
        """
        if self._find_service_config.polygon_search_mode_policy() is PolygonSearchModePolicyEnum.SearchUsingCentroid:
            # search using a centroid.
            ref_polygon = Polygon(location.vertices)
            pt_array = ref_polygon.centroid
            point = Point()
            point.longitude = pt_array.x
            point.latitude = pt_array.y
            point.spatial_ref = location.spatial_ref

            if pt_array is None:
                return None

            return self.find_service_for_point(service_urn, point, return_shape)
        else:
            ADD_DATA_REQUESTED = False
            ADD_DATA_SERVICE = self._find_service_config.additional_data_uri()
            buffer_distance = self._find_service_config.additional_data_buffer()
            if service_urn == ADD_DATA_SERVICE:
                ADD_DATA_REQUESTED = True
                esb_table = self._find_service_config.settings_for_additionaldata("data_table")
            else:
                esb_table = self._get_esb_table(service_urn)

            if ADD_DATA_REQUESTED:
                results = self._db_wrapper.get_additionaldata_for_polygon(location, esb_table, buffer_distance)
                results = self._apply_addtionaldata_multiple_match_policy(results)
                if results is None or len(results)==0:
                    results = [{'adddatauri': ''}]
            else:
                results = self._db_wrapper.get_intersecting_boundaries_for_polygon(location, esb_table)

                if (results is None or len(results) == 0) and self._find_service_config.do_expanded_search():
                    proximity_buffer = self._find_service_config.expanded_search_buffer()
                    # No results and Policy says we should buffer and research

                    results = self._db_wrapper.get_intersecting_boundaries_for_polygon(
                        location,
                        esb_table,
                        True,
                        proximity_buffer)

                results = self._apply_polygon_multiple_match_policy(results)
            return self._apply_policies(results, return_shape)

    def _apply_point_multiple_match_policy(self, mappings):
        """
        Apply the point multiple match policy to given mappings.

        :param mappings: The mappings returned from a point search.
        :type mappings ``list`` of ``dict``
        :return: Mapping list adjusted according to the point multiple match policy.
        :rtype: ``list`` of ``dict``
        """

        if mappings is not None:
            point_multiple_match_policy = self._find_service_config.point_multiple_match_policy()

            if point_multiple_match_policy == PointMultipleMatchPolicyEnum.ReturnLimitWarning:
                i = len(mappings)
                limit = self._find_service_config.point_result_limit_policy()
                if i > limit:
                    # Results exceeds configurable setting - cut off results and apply warning
                    del mappings[limit:i]
                    [mapping.update({'tooManyMappings': True}) for mapping in mappings]
            elif point_multiple_match_policy == PointMultipleMatchPolicyEnum.ReturnFirst:
                i = len(mappings)
                del mappings[1:i]  # removes items starting at 1 until the end of the list
            elif point_multiple_match_policy == PointMultipleMatchPolicyEnum.ReturnError:
                logger.warning('Multiple results matched request location.')
                raise InternalErrorException('Multiple results matched request location.')

        return mappings

    def _apply_polygon_multiple_match_policy(self, mappings):
        """
        Apply the polygon multiple match policy to given mappings.

        :param mappings: The mappings returned from a point search.
        :type mappings ``list`` of ``dict``
        :return: Mapping list adjusted according to the polygon multiple match policy.
        :rtype: ``list`` of ``dict``
        """

        if mappings is not None:
            polygon_multiple_match_policy = self._find_service_config.polygon_multiple_match_policy()

            if polygon_multiple_match_policy == PolygonMultipleMatchPolicyEnum.ReturnLimitWarning:
                i = len(mappings)
                limit = self._find_service_config.polygon_result_limit_policy()
                if i > limit:
                    # Results exceeds configurable setting - cut off results and apply warning
                    del mappings[limit:i]
                    [mapping.update({'tooManyMappings': True}) for mapping in mappings]

            elif polygon_multiple_match_policy == PolygonMultipleMatchPolicyEnum.ReturnFirst:
                i = len(mappings)
                del mappings[1:i]  # removes items starting at 1 until the end of the list
            elif polygon_multiple_match_policy == PolygonMultipleMatchPolicyEnum.ReturnAreaMajority:
                # Find and return Max area
                max_area_item = max(mappings, key=lambda x: x['AREA_RET'])
                mappings = [max_area_item]

        return mappings

    def _apply_addtionaldata_multiple_match_policy(self, mappings):
        """
        Apply the a addtional data multiple match policy to given mappings.

        :param mappings: The mappings returned from a point search.
        :type mappings ``list`` of ``dict``
        :return: Mapping list adjusted according to the match policy.
        :rtype: ``list`` of ``dict``
        """

        if mappings is not None:
            i = len(mappings)
            limit = self._find_service_config.additionaldata_result_limit()
            if i > limit:
                # Results exceeds configurable setting - cut off results and apply warning
                del mappings[limit:i]
                [mapping.update({'tooManyMappings': True}) for mapping in mappings]

        return mappings

    def _apply_policies(self, mappings, return_shape):
        """
        Applies additional polices to the mappings, e.g. expiration, additional cleanup.

        :param mappings: The mappings returned from a point search.
        :type mappings ``list`` of ``dict``
        :param return_shape: Whether or not to return the geometries of found mappings.
        :type return_shape: ``bool``
        :return: Mapping list adjusted according to the expiration policy.
        :rtype: ``list`` of ``dict``
        """

        if mappings is not None:
            for mapping in mappings:
                if mapping.get('serviceurn'):
                    mapping['expiration'] = self._get_service_expiration_policy(mapping['serviceurn'])
                self.apply_service_boundary_policy(mapping, return_shape)

        return mappings

    def apply_service_boundary_policy(self, mapping, return_shape):
        """
        Apply the service boundary policy to result mappings.

        :param mapping: A mapping returned from a point search.
        :type mapping: ``list`` of ``dict``
        :param return_shape: Whether or not to return the geometries of found mappings.
        :type return_shape: ``bool``
        :return: The mapping with fixed-up GML
        """

        # TODO -
        # Simplify - On
        # Simplify -Off
        # ReturnUnedited - Done
        # ReturnAreaMajorityPolygon
        # ReturnAllAsSinglePolygons

        GML_URN = 'http://www.opengis.net/gml'
        GML_URN_COORDS = '{0}{1}{2}'.format('{', GML_URN, '}')

        if return_shape and 'ST_AsGML_1' in mapping:
            gml = mapping['ST_AsGML_1']
            gml = gml.replace('>', ' xmlns:gml="http://www.opengis.net/gml">', 1)
            root = etree.XML(gml)

            count = 0
            for node in root.iter():
                if node.tag == '{0}MultiSurface'.format(GML_URN_COORDS):
                    attr_srs = node.attrib
                if node.tag == '{0}Polygon'.format(GML_URN_COORDS):
                    polygontxt = etree.tostring(node)
                    count = count + 1
            # If we need to do simplification, let's do it now as the last step, before we move on.
            simplify = self._find_service_config.do_polygon_simplification()
            if simplify:  # IT'S SO SIMPLE
                mapping = self._geomutil.simplify_polygon(
                    mapping_object=mapping,
                    tolerance=self._find_service_config.simplification_tolerance())

            if count > 1:
                # TODO Multipolygons - Not supported currently so just return unedited GML
                return mapping

            # We already edited the GML from simplification. Let's not do it again.
            if simplify is False:
                modified_root = etree.XML(polygontxt)
                modified_root.set('srsName', attr_srs.get('srsName', 'EPSG:4326'))
                modified_root = self._clear_attributes(modified_root)

                # Update value with new GML
                mapping['ST_AsGML_1'] = etree.tostring(modified_root).decode("utf-8")

        return mapping

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

    def _get_service_expiration_policy(self, service_urn):
        """
        Gets the expiration policy for the given service.

        :param service_urn: The identifier for the service to look up.
        :type service_urn: ``str``
        :return: The service boundary expiration string.
        :rtype: ``str``
        """
        service = self._get_esb_table(service_urn)
        policy = self._find_service_config.settings_for_service(service)

        expires_policy = policy['service_expire_policy']
        expires_string = ''

        # Based on setting Set Expires to: currentTime + TimeSpan setting or "NO-CACHE" or "NO-EXPIRATION"
        if ServiceExpiresPolicyEnum[expires_policy] == ServiceExpiresPolicyEnum.TimeSpan:
            # Expected to be in UTC format plus timespan (minutes) interval setting 2010-05-18T16:47:55.9620000-06:00
            expires_timespan = policy['service_cache_timespan']
            mapping_expires = datetime.datetime.now(tz=pytz.utc) + datetime.timedelta(
                minutes=int(expires_timespan))
            expires_string = mapping_expires.isoformat()
        elif ServiceExpiresPolicyEnum[expires_policy] == ServiceExpiresPolicyEnum.NoCache:
            expires_string = 'NO-CACHE'
        elif ServiceExpiresPolicyEnum[expires_policy] == ServiceExpiresPolicyEnum.NoExpiration:
            expires_string = 'NO-EXPIRATION'

        return expires_string


class FindServiceOuter(object):
    """
    A class to handle the tasks related to unwrapping findService requests and packaging up responses.

    """
    @inject
    def __init__(self, config: FindServiceConfigWrapper, inner: FindServiceInner):
        """
        Constructor.

        :param config: The FindService configuration wrapper object.
        :type config: :py:class:`lostservice.handling.FindServiceConfigWrapper`
        :param inner: The inner implementation class.
        :type inner: :py:class:`lostservice.handling.FindServiceInner`
        """
        self._inner = inner
        self._find_service_config = config

    def _check_is_loopback(self, path):
        if self._find_service_config.source_uri() in path:
            raise LoopException("LoopError")

    def find_service_for_point(self, request):
        """
        Find service for a point.

        :param request:  A findService request object with a point location.
        :type request :py:class:`lostservice.model.requests.FindServiceRequest`
        :return: A findService response.
        :rtype: :py:class:`lostservice.model.responses.FindServiceResponse`
        """
        self._check_is_loopback(request.path)
        include_boundary_value = self._apply_override_policy(request)

        mappings = self._inner.find_service_for_point(
            request.service,
            request.location.location,
            include_boundary_value
        )
        return_value = {'latitude': request.location.location.latitude,
                        'longitude': request.location.location.longitude,
                        'response': self._build_response(request.path,
                                                         request.location.id,
                                                         mappings,
                                                         request.nonlostdata,
                                                         include_boundary_value)}

        return return_value

    def find_service_for_civicaddress(self, request):
        """
        Find service for a civic address.
        :param request:  A findService request object with a civic address location.
        :type request :py:class:`lostservice.model.requests.FindServiceRequest`
        :return: A findService response.
        :rtype: :py:class:`lostservice.model.responses.FindServiceResponse`
        """
        self._check_is_loopback(request.path)
        include_boundary_value = self._apply_override_policy(request)

        # returns mappings and lon and lat for logging
        inner_result = self._inner.find_service_for_civicaddress(
            request,
            include_boundary_value
        )
        return_value = {'latitude':  inner_result['latitude'],
                        'longitude': inner_result['longitude'],
                        'response': self._build_response(request.path,
                                                         request.location.id,
                                                         inner_result['mappings'],
                                                         request.nonlostdata,
                                                         include_boundary_value)}

        return return_value

    def find_service_for_circle(self, request):
        """
        Find service for a circle.

        :param request:  A findService request object with a point location.
        :type request :py:class:`lostservice.model.requests.FindServiceRequest`
        :return: A findService response.
        :rtype: :py:class:`lostservice.model.responses.FindServiceResponse`
        """
        self._check_is_loopback(request.path)
        include_boundary_value = self._apply_override_policy(request)
        mappings = self._inner.find_service_for_circle(
            request.service,
            request.location.location,
            include_boundary_value
        )
        return_value = {'latitude': request.location.location.latitude,
                        'longitude': request.location.location.longitude,
                        'response': self._build_response(request.path,
                                                         request.location.id,
                                                         mappings,
                                                         request.nonlostdata,
                                                         include_boundary_value)}
        return return_value

    def find_service_for_ellipse(self, request):
        """
        Find service for an ellipse.

        :param request:  A findService request object with a point location.
        :type request :py:class:`lostservice.model.requests.FindServiceRequest`
        :return: A findService response.
        :rtype: :py:class:`lostservice.model.responses.FindServiceResponse`
        """
        self._check_is_loopback(request.path)
        include_boundary_value = self._apply_override_policy(request)
        mappings = self._inner.find_service_for_ellipse(
            request.service,
            request.location.location,
            include_boundary_value
        )

        return_value = {'latitude': request.location.location.latitude,
                        'longitude': request.location.location.longitude,
                        'response': self._build_response(request.path,
                                                         request.location.id,
                                                         mappings,
                                                         request.nonlostdata,
                                                         include_boundary_value)}
        return return_value

    def find_service_for_arcband(self, request):
        """
        Find service for an arcband.

        :param request:  A findService request object with a point location.
        :type request :py:class:`lostservice.model.requests.FindServiceRequest`
        :return: A findService response.
        :rtype: :py:class:`lostservice.model.responses.FindServiceResponse`
        """
        self._check_is_loopback(request.path)
        include_boundary_value = self._apply_override_policy(request)
        mappings = self._inner.find_service_for_arcband(
            request.service,
            request.location.location,
            include_boundary_value
        )
        return_value = {}
        try:
            lat = request.location.location.build_shapely_geometry().representative_point().y
            long = request.location.location.build_shapely_geometry().representative_point().x
            resp = self._build_response(request.path, request.location.id,
                                        mappings, request.nonlostdata, include_boundary_value)

            return_value = {'latitude': lat,
                            'longitude': long,
                            'response': resp}

        except Exception as e:
            logger.error(e)

        return return_value

    def find_service_for_polygon(self, request):
        """
        Find service for an arcband.

        :param request:  A findService request object with a point location.
        :type request :py:class:`lostservice.model.requests.FindServiceRequest`
        :return: A findService response.
        :rtype: :py:class:`lostservice.model.responses.FindServiceResponse`
        """
        self._check_is_loopback(request.path)
        include_boundary_value = self._apply_override_policy(request)
        mappings = self._inner.find_service_for_polygon(
            request.service,
            request.location.location,
            include_boundary_value
        )
        return_value = {}
        try:
            lat = request.location.location.build_shapely_geometry().centroid.y
            long = request.location.location.build_shapely_geometry().centroid.x
            resp = self._build_response(request.path, request.location.id,
                                        mappings, request.nonlostdata, include_boundary_value)
            return_value = {'latitude': lat,
                            'longitude': long,
                            'response': resp}
        except Exception as e:
            logger.error(e)

        return return_value

    def _build_response(self, path, location_used, mappings, nonlostdata, include_boundary_value=False):
        """
        Builds a find service response.

        :param path: The list of path elements that came in with the request.
        :type path: ``list`` of ``str``
        :param location_used: The location id that came in with the request.
        :type location_used: ``str``
        :param mappings: A list of all mappings returned by the query.
        :type mappings: ``list`` of ``dict``
        :param nonlostdata: Pass-through elements from the request.
        :type nonlostdata: ``list``
        :return:  A FindServiceResponse
        :rtype: :py:class:`lostservice.model.responses.FindServiceResponse`
        """
        response = FindServiceResponse()
        response.path = path
        response.path.append(self._find_service_config.source_uri())
        response.location_used = location_used
        response.mappings = self._build_mapping_list(mappings, include_boundary_value)

        nonlostdata = self._build_warnings(mappings, nonlostdata)
        response.nonlostdata = nonlostdata
        return response

    def _build_warnings(self, mappings, nonlostdata):
        """
        Builds warning element if needed.
        :param mappings: A list of all mappings returned by the query.
        :param nonlostdata: Pass-through elements from the request.
        :return:
        """

        if mappings is None:
            return nonlostdata
        xml_warning = None
        multiple_match = self._find_service_config.polygon_multiple_match_policy()
        source_uri = self._find_service_config.source_uri()
        # Is there additional data in our mappings?
        if self._check_is_addurl_in_mappings(mappings)or \
        (multiple_match == PolygonMultipleMatchPolicyEnum.ReturnLimitWarning):
            # Did we run into too many mappings being returned by the request?
            if self._check_too_many_mappings(mappings):
                # Setting is ReturnLimitWarning and flag was found so generate a new element for warnings and add
                # tooManyMappings as sub-element.  Place this in nonlostdata as another element to be added
                # to the final response.
                LOST_URN = 'urn:ietf:params:xml:ns:lost1'
                xml_warning = etree.Element('warnings', nsmap={None: LOST_URN}, attrib={'source': source_uri})

                # add to the warnings element
                warnings_element = etree.SubElement(xml_warning, 'tooManyMappings',
                    attrib={'message': 'Mapping limit exceeded, mappings returned have been truncated.'})

                attr = warnings_element.attrib
                attr['{http://www.w3.org/XML/1998/namespace}lang'] = 'en'
        # Did we have to use a fuzzy match instead of an exact match?
        if self._check_fuzzy_match_used():
            xml_warning = etree.Element('warnings', attrib={'source': source_uri})
            etree.SubElement(xml_warning, 'approximateLocationUsed',
                 attrib={'message': 'An exact match could not be found, but a point in near accuracy was used to find '
                         'the service boundary.'})
        # Did we end up with a default route?
        if self._check_using_default_route(mappings):
            # check if the warnings tag has already been added
            if len(nonlostdata) > 0:
                xml_warning = nonlostdata[0].find('warnings')
            if not xml_warning:
                xml_warning = etree.Element('warnings', attrib={'source': source_uri})
            etree.SubElement(xml_warning,'defaultMappingReturned',
                attrib={'message': "Unable to determine PSAP for the given location: using default PSAP"})
        # Add all this warning stuff to our response.
        if xml_warning is not None:
            nonlostdata.append((xml_warning))

        return nonlostdata

    def _check_is_addurl_in_mappings(self, mappings) -> bool:
        """
        Check for addurl in mapping.
        :param mappings: a list of all the mappings returned by the query
        :type mappings: ``list`` of ``dict``
        :return:
        :rtype: ``bool``
        """
        for mapping in mappings:
            if 'adddatauri' in mapping:
                return True
            return False

    def _check_too_many_mappings(self, mappings) -> bool:
        """
        Check for tooManyMappings flag, which triggers building of a warning.

        :param mappings: a list of all the mappings returned by the query
        :type mappings: ``list`` of ``dict``
        :return:
        :rtype: ``bool``
        """
        for mapping in mappings:
            if 'tooManyMappings' in mapping:
                return True

        return False

    def _check_using_default_route(self, mappings) -> bool:
        """"
        Check for default_route_used  flag , which triggers building a warning
        :param mappings: a list of all the mappings returned by the query
        :type mappings: ``list`` of ``dict``
        :return:
        :rtype: ``bool``
        """
        for mapping in mappings:
            if 'default_route_used' in mapping:
                return True

        return False

    def _check_fuzzy_match_used(self) -> bool:
        """
        Checks to see if we used a fuzzy match
        :rtype: ``bool``
        """
        if self._inner is not None:
            return self._inner.fuzzy_used
        else:
            return False

    def _build_mapping_list(self, mappings, include_boundary_value=False) -> [ResponseMapping]:
        """
        Build the collection of all response mappings.

        :param mappings: A list of all mappings returned by the query.
        :type mappings: ``list`` of ``dict``
        :param include_boundary_value: Flag to control whether or not to include the mapping boundary by value.
        :type include_boundary_value: ``bool``
        :return: a list of response mappings.
        :rtype: :py:class:`[lostservice.model.responses.ResponseMapping]`
        """
        # Resolve source uri once . . .
        source_uri = self._find_service_config.source_uri()

        resp_mappings = []
        if mappings is not None:
            for mapping in mappings:
                resp_mapping = self._build_one_mapping(mapping, include_boundary_value)
                resp_mapping.source = source_uri
                resp_mappings.append(resp_mapping)

        return resp_mappings

    def _build_one_mapping(self, mapping, include_boundary_value=False) -> ResponseMapping:
        """
        Create a single ResponseMapping from a query result.

        :param mapping: A dictonary of the query result attrubtes for a mapping.
        :type mapping: ``dict``
        :param include_boundary_value: Flag to control whether or not to include the mapping boundary by value.
        :type include_boundary_value: ``bool``
        :return: A ResponseMapping instance.
        :rtype: :py:class:`lostservice.model.responses.ResponseMapping`
        """
        if 'adddatauri' in mapping:
            resp_mapping = AdditionalDataResponseMapping()
            resp_mapping.adddatauri = mapping.get('adddatauri', "")
            resp_mapping.service_urn = self._find_service_config.settings_for_additionaldata("service_urn")
        else:
            resp_mapping = ResponseMapping()
            resp_mapping.display_name = mapping['displayname']
            resp_mapping.route_uri = mapping['routeuri']
            resp_mapping.service_number = mapping['servicenum']
            resp_mapping.service_urn = mapping.get('serviceurn')

            if self._find_service_config.service_boundary_return_geodetic_override() == \
                    ServiceBoundaryGeodeticOverridePolicyEnum.ReturnNothing:
                # Do not return ServiceBoundary tag at all
                resp_mapping.boundary_value = None
            elif include_boundary_value and 'ST_AsGML_1' in mapping:
                resp_mapping.boundary_value = mapping['ST_AsGML_1']
            else:
                resp_mapping.boundary_value = ""

        if "locationValidation" in mapping:
            resp_mapping.locationValidation = mapping.get("locationValidation")

        resp_mapping.last_updated = mapping.get('updatedate', '')
        resp_mapping.expires = mapping.get('expiration', "NO-CACHE")
        resp_mapping.source_id = mapping.get('srcunqid', "")

        return resp_mapping

    def _apply_override_policy(self, request) -> bool:
        """
        Check Service boundary return override settings 
        :param request: 
        :return: to include the boundary or not
        :rtype: ``bool``
        """
        # use false for ReturnNothing - second check is done in _build_one_mapping()
        include_boundary_value = False
        geodetic_override = self._find_service_config.service_boundary_return_geodetic_override()
        if geodetic_override == ServiceBoundaryGeodeticOverridePolicyEnum.MatchRequest:
            # Respect the value in the request
            include_boundary_value = request.serviceBoundary == 'value'
        elif geodetic_override == ServiceBoundaryGeodeticOverridePolicyEnum.ReturnReference:
            # override the value in the request and never return the GML representing the shape
            include_boundary_value = False
        elif geodetic_override == ServiceBoundaryGeodeticOverridePolicyEnum.ReturnValue:
            # override the value in the request and always return the GML representing the shape
            include_boundary_value = True

        return include_boundary_value
