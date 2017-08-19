#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. currentmodule:: lostservice.handling.Listservice
.. moduleauthor:: Avinash <arayapudi@geo-comm.com>

Implementation classes for Listservice queries.
"""

import datetime
import pytz
from enum import Enum
from injector import inject
from lostservice.configuration import Configuration
from lostservice.model.responses import ResponseMapping, ListServicesByLocationResponse
import lostservice.geometry as geom
from lostservice.db.gisdb import GisDbInterface
from lxml import etree
from shapely.geometry import Polygon


PARENT_SERVICE = 'parent'
LIST_SERVICE = 'Yes'
NO_SERVICE = 'No'


# def modify_service(fun):
#     """ for modifying the server service data"""
#     def service_data(*args):
#         if args[1] == 'urn:nena:service:sos':
#             return fun(args[0], args[1], args[2], args[3], args[4], LIST_SERVICE)
#         elif args[1] is None:
#             return fun(args[0], args[1], args[2], args[3], args[4], PARENT_SERVICE)
#         elif args[1].find('.'):
#             return fun(args[0], args[1], args[2], args[3], args[4], NO_SERVICE)
#     return service_data


class ListServiceBYLocationException(Exception):
    """
    Raised when something goes wrong in the process of a ListService request.

    :param message: The exception message
    :type message:  ``str``
    :param nested: Nested exception, if any.
    :type nested:
    """
    def __init__(self, message, nested=None):
        super().__init__(message)
        self._nested = nested


class ListServiceBYLocationConfigWrapper(object):
    """
    A wrapper class for ListService configuration related information.

    """
    @inject
    def __init__(self, config: Configuration):
        """
        Constructor.

        :param config: The configuration object.
        :type config: :py:class:`lostservice.configuration.Configuration`
        """
        self._config = config

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


class ListServiceByLocationInner(object):
    """
    A class to handle the actual implementation of the various ListService requests, responsible for making calls to
    the underlying database layers as well as applying policy.

    """
    @inject
    def __init__(self, config: ListServiceBYLocationConfigWrapper, db_wrapper: GisDbInterface):
        """
        Constructor

        :param config: The ListService configuration wrapper object.
        :type config: :py:class:`lostservice.handling.ListServiceConfigWrapper`
        :param db_wrapper: The db wrapper class instance.
        :type db_wrapper: :py:class:`lostservice.db.gisdb.GisDbInterface`
        """
        self._list_service_config = config
        self._db_wrapper = db_wrapper
        self._mappings = self._db_wrapper.get_urn_table_mappings()

    def List_serviceBYlocation_for_point(self, service_urn, longitude, latitude, spatial_ref):
        """
        List services for the given point.

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
        if service_urn == 'urn:nena:service:sos':
            esb_table = self._mappings.values()
            results = self._db_wrapper.get_list_services_for_point(longitude,
                latitude,
                spatial_ref,
                esb_table)
            return [i[0].get('serviceurn') for i in results if i and i[0].get('serviceurn') != 'urn:nena:service:sos']
        elif service_urn is None:
            return ['urn:nena:service:sos']
        elif service_urn.find('.'):
            return

    def List_service_BYLocation_for_circle(self,
                                service_urn,
                                longitude,
                                latitude,
                                spatial_ref,
                                radius,
                                radius_uom,):
        """
        List services for the given circle.

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
        if service_urn == 'urn:nena:service:sos':
            esb_table = self._mappings.values()
            results = self._db_wrapper.get_intersecting_list_service_for_circle(
                longitude,
                latitude,
                spatial_ref,
                radius,
                radius_uom, esb_table)
            return [i[0].get('serviceurn') for i in results if i and i[0].get('serviceurn') != 'urn:nena:service:sos']
        elif service_urn is None:
            return ['urn:nena:service:sos']
        elif service_urn.find('.'):
            return


    def List_service_ByLocation_for_ellipse(self,
                                 longitude,
                                 latitude,
                                 spatial_ref,
                                 semi_major_axis,
                                 semi_minor_axis,
                                 orientation,):
        """
        List services for the given ellipse.

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

        esb_table = self._mappings.values()

        results = self._db_wrapper.get_list_services_for_ellipse(
            longitude,
            latitude,
            spatial_ref,
            float(semi_major_axis),
            float(semi_minor_axis),
            float(orientation),
            esb_table)
        return [i[0].get('serviceurn') for i in results if i and i[0].get('serviceurn') != 'urn:nena:service:sos']

    def list_service_ByLocation_for_arcband(self,
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
        List services for the given arcband.

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
        return self.List_service_ByLocation_for_polygon(service_urn, points, spatial_ref, return_shape)

    def List_service_ByLocation_for_polygon(self, service_urn, points, spatial_ref, return_shape=False):
        """
        Listservices for the given polygon.

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
        if service_urn == 'urn:nena:service:sos':
            esb_table = self._mappings.values()
            results = self._db_wrapper.get_intersecting_list_service_for_polygon(points, spatial_ref, esb_table)
            return [i[0].get('serviceurn') for i in results if i and i[0].get('serviceurn') != 'urn:nena:service:sos']
        elif service_urn is None:
            return ['urn:nena:service:sos']
        elif service_urn.find('.'):
            return




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


class ListServiceBylocationOuter(object):
    """
    A class to handle the tasks related to unwrapping ListService requests and packaging up responses.

    """
    @inject
    def __init__(self, config: ListServiceBYLocationConfigWrapper, inner: ListServiceByLocationInner):
        """
        Constructor.

        :param config: The ListService configuration wrapper object.
        :type config: :py:class:`lostservice.handling.ListServiceConfigWrapper`
        :param inner: The inner implementation class.
        :type inner: :py:class:`lostservice.handling.ListServiceInner`
        """
        self._inner = inner
        self._list_service_config = config

    def List_ServiceBylocation_for_point(self, request):
        """
        List service for a point.

        :param request:  A ListService request object with a point location.
        :type request :py:class:`lostservice.model.requests.ListServiceRequest`
        :return: A ListService response.
        :rtype: :py:class:`lostservice.model.responses.ListServiceResponse`
        """
        mappings = self._inner.List_serviceBYlocation_for_point(
            request.service,
            request.location.location.longitude,
            request.location.location.latitude,
            request.location.location.spatial_ref
        )
        return self._build_response(request.path,
                                    request.location.id,
                                    mappings,
                                    request.nonlostdata)

    def List_serviceBylocation_for_circle(self, request):
        """
        List service for a circle.

        :param request:  A ListService request object with a point location.
        :type request :py:class:`lostservice.model.requests.ListServiceRequest`
        :return: A ListService response.
        :rtype: :py:class:`lostservice.model.responses.ListServiceResponse`
        """
        mappings = self._inner.List_service_BYLocation_for_circle(
            request.service,
            request.location.location.longitude,
            request.location.location.latitude,
            request.location.location.spatial_ref,
            float(request.location.location.radius),
            request.location.location.uom)
        return self._build_response(request.path,
                                    request.location.id,
                                    mappings,
                                    request.nonlostdata)

    def List_serviceBylocation_for_ellipse(self, request):
        """
        List service for an ellipse.

        :param request:  A ListService request object with a point location.
        :type request :py:class:`lostservice.model.requests.ListServiceRequest`
        :return: A ListService response.
        :rtype: :py:class:`lostservice.model.responses.ListServiceResponse`
        """
        mappings = self._inner.List_service_ByLocation_for_ellipse(
            request.location.location.longitude,
            request.location.location.latitude,
            request.location.location.spatial_ref,
            float(request.location.location.semiMajorAxis),
            float(request.location.location.semiMinorAxis),
            float(request.location.location.orientation))
        return self._build_response(request.path,
                                    request.location.id,
                                    mappings,
                                    request.nonlostdata)

    def List_serviceBylocation_for_arcband(self, request):
        """
        List service for an arcband.

        :param request:  A ListService request object with a point location.
        :type request :py:class:`lostservice.model.requests.ListServiceRequest`
        :return: A ListService response.
        :rtype: :py:class:`lostservice.model.responses.ListServiceResponse`
        """
        mappings = self._inner.list_service_ByLocation_for_arcband(
            request.service,
            request.location.location.longitude,
            request.location.location.latitude,
            request.location.location.spatial_ref,
            float(request.location.location.start_angle),
            float(request.location.location.opening_angle),
            float(request.location.location.inner_radius),
            float(request.location.location.outer_radius))
        return self._build_response(request.path,
                                    request.location.id,
                                    mappings,
                                    request.nonlostdata)

    def List_serviceBylocation_for_polygon(self, request):
        """
        List service for an arcband.

        :param request:  A ListService request object with a point location.
        :type request :py:class:`lostservice.model.requests.ListServiceRequest`
        :return: A ListService response.
        :rtype: :py:class:`lostservice.model.responses.ListServiceResponse`
        """
        mappings = self._inner.List_service_ByLocation_for_polygon(
            request.service,
            request.location.location.vertices,
            request.location.location.spatial_ref
        )
        return self._build_response(request.path,
                                    request.location.id,
                                    mappings,
                                    request.nonlostdata)

    def _build_response(self, path, location_id, mapping,  nonlostdata):
        """
        Builds a List service response.

        :param path: The list of path elements that came in with the request.
        :type path: ``list`` of ``str``
        :param location_used: The location id that came in with the request.
        :type location_used: ``str``
        :param mappings: A list of all mappings returned by the query.
        :type mappings: ``list`` of ``dict``
        :param nonlostdata: Passthrough elements from the request.
        :type nonlostdata: ``list``
        :return:  A ListServiceResponse
        :rtype: :py:class:`lostservice.model.responses.ListServiceResponse`
        """
        response = ListServicesByLocationResponse()
        response.services = mapping
        response.path = path
        response.path.append(self._list_service_config.source_uri())
        response.location_id = location_id
        response.nonlostdata = nonlostdata
        return response

    def _build_mapping_list(self, mappings):
        """
        Build the collection of all response mappings.

        :param mappings: A list of all mappings returned by the query.
        :type mappings: ``list`` of ``dict``
        :param include_boundary_value: Flag to control whether or not to include the mapping boundary by value.
        :type include_boundary_value: ``bool``
        :return:
        """
        # Resolve source uri once . . .
        source_uri = self._list_service_config.source_uri()

        resp_mappings = []
        for mapping in mappings:
            resp_mapping = self._build_one_mapping(mapping)
            resp_mapping.source = source_uri
            resp_mappings.append(resp_mapping)

        return resp_mappings

    def _build_one_mapping(self, mapping):
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
        return resp_mapping
