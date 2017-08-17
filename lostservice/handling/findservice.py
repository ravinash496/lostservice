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
from lostservice.model.responses import FindServiceResponse, ResponseMapping
import lostservice.geometry as geom
from lostservice.db.gisdb import GisDbInterface
from lxml import etree
from shapely.geometry import Polygon


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

    def source_uri(self):
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


class FindServiceInner(object):
    """
    A class to handle the actual implementation of the various findService requests, responsible for making calls to
    the underlying database layers as well as applying policy.

    """
    @inject
    def __init__(self, config: FindServiceConfigWrapper, db_wrapper: GisDbInterface):
        """
        Constructor

        :param config: The FindService configuration wrapper object.
        :type config: :py:class:`lostservice.handling.FindServiceConfigWrapper`
        :param db_wrapper: The db wrapper class instance.
        :type db_wrapper: :py:class:`lostservice.db.gisdb.GisDbInterface`
        """
        self._find_service_config = config
        self._db_wrapper = db_wrapper
        self._mappings = self._db_wrapper.get_urn_table_mappings()

    def find_service_for_point(self, service_urn, longitude, latitude, spatial_ref, return_shape=False):
        """
        Find services for the given point.

        :param service_urn: The identifier for the service to look up.
        :type service_urn: ``str``
        :param longitude: Longitude of the point to search.
        :type longitude: ``float``
        :param latitude: Latitude of the point to search.
        :type latitude: ``float``
        :param spatial_ref: Spatial reference of the point to search.
        :type spatial_ref: ``str``
        :param return_shape: Whether or not to return the geometries of found mappings.
        :type return_shape: ``bool``
        :return: The service mappings for the given point.
        :rtype: ``list`` of ``dict``
        """
        esb_table = self._mappings[service_urn]

        results = self._db_wrapper.get_containing_boundary_for_point(
            longitude,
            latitude,
            spatial_ref,
            esb_table)

        if results is not None and len(results) != 0:
            results = self._apply_point_multiple_match_policy(results)
        elif self._find_service_config.do_expanded_search():

            multiple_match_policy = self._find_service_config.polygon_multiple_match_policy()
            return_area = multiple_match_policy is PolygonMultipleMatchPolicyEnum.ReturnAreaMajority
            proximity_buffer = self._find_service_config.expanded_search_buffer()

            results = self._db_wrapper.get_intersecting_boundaries_for_circle(
                longitude,
                latitude,
                spatial_ref,
                proximity_buffer,
                None,  # TODO, what is our UOM for buffers, assert meters?
                esb_table,
                return_area,
                return_shape)

            results = self._apply_polygon_multiple_match_policy(results)

        return self._apply_policies(results, return_shape)

    def find_service_for_circle(self,
                                service_urn,
                                longitude,
                                latitude,
                                spatial_ref,
                                radius,
                                radius_uom,
                                return_shape=False):
        """
        Find services for the given circle.

        :param service_urn: The identifier for the service to look up.
        :type service_urn: ``str``
        :param longitude: Longitude of the center of the circle to search.
        :type longitude: ``float``
        :param latitude: Latitude of the center of the circle to search.
        :type latitude: ``float``
        :param spatial_ref: Spatial reference of the center of the circle to search.
        :type spatial_ref: ``str``
        :param radius: The radius of the circle to search.
        :type radius: ``float``
        :param radius_uom: Unit of measure for the radius.
        :type radius_uom: ``str``
        :param return_shape: Whether or not to return the geometries of found mappings.
        :type return_shape: ``bool``
        :return: The service mappings for the given circle.
        :rtype: ``list`` of ``dict``
        """
        esb_table = self._mappings[service_urn]

        multiple_match_policy = self._find_service_config.polygon_multiple_match_policy()
        return_area = multiple_match_policy is PolygonMultipleMatchPolicyEnum.ReturnAreaMajority

        results = self._db_wrapper.get_intersecting_boundaries_for_circle(
            longitude,
            latitude,
            spatial_ref,
            radius,
            radius_uom, esb_table, return_area, return_shape)

        if (results is None or len(results) == 0) and self._find_service_config.do_expanded_search():
            proximity_buffer = self._find_service_config.expanded_search_buffer()
            results = self._db_wrapper.get_intersecting_boundaries_for_circle(
                longitude,
                latitude,
                spatial_ref,
                radius,
                radius_uom,
                esb_table,
                return_area,
                return_shape,
                True,
                proximity_buffer)

        results = self._apply_polygon_multiple_match_policy(results)
        return self._apply_policies(results, return_shape)

    def find_service_for_ellipse(self,
                                 service_urn,
                                 longitude,
                                 latitude,
                                 spatial_ref,
                                 semi_major_axis,
                                 semi_minor_axis,
                                 orientation,
                                 return_shape=False):
        """
        Find services for the given ellipse.

        :param service_urn: The identifier for the service to look up.
        :type service_urn: ``str``
        :param longitude: Longitude of the center of the ellipse to search.
        :type longitude: ``float``
        :param latitude: Latitude of the center of the ellipse to search.
        :type latitude: ``float``
        :param spatial_ref: Spatial reference of the center of the ellipse to search.
        :type spatial_ref: ``str``
        :param semi_major_axis: The length of the semi-major axis.
        :type semi_major_axis: ``float``
        :param semi_minor_axis: The length of the semi-minor axis.
        :type semi_minor_axis: ``float``
        :param orientation: The orientation of the ellipse.
        :type orientation: ``float``
        :param return_shape: Whether or not to return the geometries of found mappings.
        :type return_shape: ``bool``
        :return: The service mappings for the given ellipse.
        :rtype: ``list`` of ``dict``
        """
        # TODO: does there need to be an orientation UOM?
        # TODO: Why do the ellipse queries always return the intersection areas but others don't?

        esb_table = self._mappings[service_urn]

        results = self._db_wrapper.get_intersecting_boundary_for_ellipse(
            longitude,
            latitude,
            spatial_ref,
            semi_major_axis,
            semi_minor_axis,
            orientation,
            esb_table)

        if (results is None or len(results) == 0) and self._find_service_config.do_expanded_search():
            # No results and Policy says we should buffer and research
            proximity_buffer = self._find_service_config.expanded_search_buffer()

            results = self._db_wrapper.get_intersecting_boundary_for_ellipse(
                longitude,
                latitude,
                spatial_ref,
                semi_major_axis + proximity_buffer,
                semi_minor_axis + proximity_buffer,
                orientation,
                esb_table)

        results = self._apply_polygon_multiple_match_policy(results)
        return self._apply_policies(results, return_shape)

    def find_service_for_arcband(self,
                                 service_urn,
                                 longitude,
                                 latitude,
                                 spatial_ref,
                                 start_angle,
                                 opening_angle,
                                 inner_radius,
                                 outer_radius,
                                 return_shape=False):
        """
        Find services for the given arcband.

        :param service_urn: The identifier for the service to look up.
        :type service_urn: ``str``
        :param longitude: Longitude of the center of the arcband to search.
        :type longitude: ``float``
        :param latitude: Latitude of the center of the arcband to search.
        :type latitude: ``float``
        :param spatial_ref: Spatial reference of the arcband to search.
        :type spatial_ref: ``str``
        :param start_angle: The angle to the start of the ellipse (from north).
        :type start_angle: ``float``
        :param opening_angle: The sweep of the arc.
        :type opening_angle: ``float``
        :param inner_radius: The inner radius of the arcband.
        :type inner_radius: ``float``
        :param outer_radius: The outer radius of the arcband.
        :type outer_radius: ``float``
        :param return_shape: Whether or not to return the geometries of found mappings.
        :type return_shape: ``bool``
        :return: The service mappings for the given arcband.
        :rtype: ``list`` of ``dict``
        """
        arcband = geom.generate_arcband(longitude, latitude, start_angle, opening_angle, inner_radius, outer_radius)
        points = geom.get_vertices_for_geom(arcband)[0]
        return self.find_service_for_polygon(service_urn, points, spatial_ref, return_shape)

    def find_service_for_polygon(self, service_urn, points, spatial_ref, return_shape=False):
        """
        Find services for the given polygon.

        :param service_urn: The identifier for the service to look up.
        :type service_urn: ``str``
        :param points: A list of vertices in (x,y) format.
        :type points: ``list``
        :param spatial_ref: Spatial reference of the polygon to search.
        :type spatial_ref: ``str``
        :param return_shape: Whether or not to return the geometries of found mappings.
        :type return_shape: ``bool``
        :return: The service mappings for the given polygon.
        :rtype: ``list`` of ``dict``
        """
        if self._find_service_config.polygon_search_mode_policy() is PolygonSearchModePolicyEnum.SearchUsingCentroid:
            # search using a centroid.
            ref_polygon = Polygon(points)
            pt_array = ref_polygon.centroid

            if pt_array is None:
                return None

            return self.find_service_for_point(service_urn, pt_array.x, pt_array.y, spatial_ref, return_shape)
        else:
            esb_table = self._mappings[service_urn]
            results = self._db_wrapper.get_intersecting_boundaries_for_polygon(points, spatial_ref, esb_table)

            if (results is None or len(results) == 0) and self._find_service_config.do_expanded_search():
                proximity_buffer = self._find_service_config.expanded_search_buffer()
                # No results and Policy says we should buffer and research

                results = self._db_wrapper.get_intersecting_boundaries_for_polygon(
                    points,
                    spatial_ref,
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
        point_multiple_match_policy = self._find_service_config.point_multiple_match_policy()

        if point_multiple_match_policy == PointMultipleMatchPolicyEnum.ReturnAllLimit5:
            i = len(mappings)
            del mappings[5:i]  # removes items starting at 5 until the end of the list
        elif point_multiple_match_policy == PointMultipleMatchPolicyEnum.ReturnFirst:
            i = len(mappings)
            del mappings[1:i]  # removes items starting at 1 until the end of the list
        elif point_multiple_match_policy == PointMultipleMatchPolicyEnum.ReturnError:
            raise FindServiceException('Multiple results matched request location')

        return mappings

    def _apply_polygon_multiple_match_policy(self, mappings):
        """
        Apply the polygon multiple match policy to given mappings.

        :param mappings: The mappings returned from a point search.
        :type mappings ``list`` of ``dict``
        :return: Mapping list adjusted according to the polygon multiple match policy.
        :rtype: ``list`` of ``dict``
        """
        polygon_multiple_match_policy = self._find_service_config.polygon_multiple_match_policy()

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

        return mappings

    def _apply_policies(self, mappings, return_shape):
        """
        Sets the expiration of each mapping according to configuration.

        :param mappings: The mappings returned from a point search.
        :type mappings ``list`` of ``dict``
        :param return_shape: Whether or not to return the geometries of found mappings.
        :type return_shape: ``bool``
        :return: Mapping list adjusted according to the expiration policy.
        :rtype: ``list`` of ``dict``
        """
        for mapping in mappings:
            mapping['expiration'] = self._get_service_expiration_policy(mapping['serviceurn'])
            self._apply_service_boundary_policy(mapping, return_shape)

        return mappings

    def _apply_service_boundary_policy(self, mapping, return_shape):
        """
        Apply the service boundary policy to result mappings.

        :param mapping: A mapping returned from a search.
        :type mapping ``dict``
        :param return_shape: Whether or not to return the geometries of found mappings.
        :type return_shape: ``bool``
        :return:
        """

        # TODO -
        # Simplify - On
        # Simplify -Off
        # ReturnUnedited - Done
        # ReturnAreaMajorityPolygon
        # ReturnAllAsSinglePolygons

        if return_shape and 'ST_AsGML_1' in mapping:
            gml = mapping['ST_AsGML_1']
            gml = gml.replace('>', ' xmlns:gml="http://www.opengis.net/gml">', 1)

            root = etree.XML(gml)
            root = self._clear_attributes(root)

            # Update value with new GML
            mapping['ST_AsGML_1'] = etree.tostring(root).decode("utf-8")

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
        service = self._mappings[service_urn]
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

    def find_service_for_point(self, request):
        """
        Find service for a point.

        :param request:  A findService request object with a point location.
        :type request :py:class:`lostservice.model.requests.FindServiceRequest`
        :return: A findService response.
        :rtype: :py:class:`lostservice.model.responses.FindServiceResponse`
        """
        include_boundary_value = request.serviceBoundary == 'value'
        mappings = self._inner.find_service_for_point(
            request.service,
            request.location.location.longitude,
            request.location.location.latitude,
            request.location.location.spatial_ref,
            include_boundary_value
        )
        return self._build_response(request.path,
                                    request.location.id,
                                    mappings,
                                    request.nonlostdata,
                                    include_boundary_value)

    def find_service_for_circle(self, request):
        """
        Find service for a circle.

        :param request:  A findService request object with a point location.
        :type request :py:class:`lostservice.model.requests.FindServiceRequest`
        :return: A findService response.
        :rtype: :py:class:`lostservice.model.responses.FindServiceResponse`
        """
        include_boundary_value = request.serviceBoundary == 'value'
        mappings = self._inner.find_service_for_circle(
            request.service,
            request.location.location.longitude,
            request.location.location.latitude,
            request.location.location.spatial_ref,
            float(request.location.location.radius),
            request.location.location.uom,
            include_boundary_value
        )
        return self._build_response(request.path,
                                    request.location.id,
                                    mappings,
                                    request.nonlostdata,
                                    include_boundary_value)

    def find_service_for_ellipse(self, request):
        """
        Find service for an ellipse.

        :param request:  A findService request object with a point location.
        :type request :py:class:`lostservice.model.requests.FindServiceRequest`
        :return: A findService response.
        :rtype: :py:class:`lostservice.model.responses.FindServiceResponse`
        """
        include_boundary_value = request.serviceBoundary == 'value'
        mappings = self._inner.find_service_for_ellipse(
            request.service,
            request.location.location.longitude,
            request.location.location.latitude,
            request.location.location.spatial_ref,
            float(request.location.location.semiMajorAxis),
            float(request.location.location.semiMinorAxis),
            float(request.location.location.orientation),
            include_boundary_value
        )
        return self._build_response(request.path,
                                    request.location.id,
                                    mappings,
                                    request.nonlostdata,
                                    include_boundary_value)

    def find_service_for_arcband(self, request):
        """
        Find service for an arcband.

        :param request:  A findService request object with a point location.
        :type request :py:class:`lostservice.model.requests.FindServiceRequest`
        :return: A findService response.
        :rtype: :py:class:`lostservice.model.responses.FindServiceResponse`
        """
        include_boundary_value = request.serviceBoundary == 'value'
        mappings = self._inner.find_service_for_arcband(
            request.service,
            request.location.location.longitude,
            request.location.location.latitude,
            request.location.location.spatial_ref,
            float(request.location.location.start_angle),
            float(request.location.location.opening_angle),
            float(request.location.location.inner_radius),
            float(request.location.location.outer_radius),
            include_boundary_value
        )
        return self._build_response(request.path,
                                    request.location.id,
                                    mappings,
                                    request.nonlostdata,
                                    include_boundary_value)

    def find_service_for_polygon(self, request):
        """
        Find service for an arcband.

        :param request:  A findService request object with a point location.
        :type request :py:class:`lostservice.model.requests.FindServiceRequest`
        :return: A findService response.
        :rtype: :py:class:`lostservice.model.responses.FindServiceResponse`
        """
        include_boundary_value = request.serviceBoundary == 'value'
        mappings = self._inner.find_service_for_polygon(
            request.service,
            request.location.location.vertices,
            request.location.location.spatial_ref,
            include_boundary_value
        )
        return self._build_response(request.path,
                                    request.location.id,
                                    mappings,
                                    request.nonlostdata,
                                    include_boundary_value)

    def _build_response(self, path, location_used, mappings, nonlostdata, include_boundary_value=False):
        """
        Builds a find service response.

        :param path: The list of path elements that came in with the request.
        :type path: ``list`` of ``str``
        :param location_used: The location id that came in with the request.
        :type location_used: ``str``
        :param mappings: A list of all mappings returned by the query.
        :type mappings: ``list`` of ``dict``
        :param nonlostdata: Passthrough elements from the request.
        :type nonlostdata: ``list``
        :return:  A FindServiceResponse
        :rtype: :py:class:`lostservice.model.responses.FindServiceResponse`
        """
        response = FindServiceResponse()
        response.path = path
        response.path.append(self._find_service_config.source_uri())
        response.location_used = location_used
        response.mappings = self._build_mapping_list(mappings, include_boundary_value)
        response.nonlostdata = nonlostdata
        return response

    def _build_mapping_list(self, mappings, include_boundary_value=False):
        """
        Build the collection of all response mappings.

        :param mappings: A list of all mappings returned by the query.
        :type mappings: ``list`` of ``dict``
        :param include_boundary_value: Flag to control whether or not to include the mapping boundary by value.
        :type include_boundary_value: ``bool``
        :return:
        """
        # Resolve source uri once . . .
        source_uri = self._find_service_config.source_uri()

        resp_mappings = []
        for mapping in mappings:
            resp_mapping = self._build_one_mapping(mapping, include_boundary_value)
            resp_mapping.source = source_uri
            resp_mappings.append(resp_mapping)

        return resp_mappings

    def _build_one_mapping(self, mapping, include_boundary_value=False):
        """
        Create a single ResponseMapping from a query result.

        :param mapping: A dictonary of the query result attrubtes for a mapping.
        :type mapping: ``dict``
        :param include_boundary_value: Flag to control whether or not to include the mapping boundary by value.
        :type include_boundary_value: ``bool``
        :return: A ResponseMapping instance.
        :rtype: :py:class:`lostservice.model.responses.ResponseMapping`
        """
        resp_mapping = ResponseMapping()
        resp_mapping.display_name = mapping['displayname']
        resp_mapping.route_uri = mapping['routeuri']
        resp_mapping.service_number = mapping['servicenum']
        resp_mapping.source_id = mapping['gcunqid']
        resp_mapping.service_urn = mapping['serviceurn']
        resp_mapping.last_updated = mapping['updatedate']
        resp_mapping.expires = mapping['expiration']

        if include_boundary_value and 'ST_AsGML_1' in mapping:
            resp_mapping.boundary_value = mapping['ST_AsGML_1']

        return resp_mapping










