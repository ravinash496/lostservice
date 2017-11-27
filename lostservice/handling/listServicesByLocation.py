#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. currentmodule:: lostservice.handling.Listservice
.. moduleauthor:: Avinash <arayapudi@geo-comm.com>

Implementation classes for Listservice queries.
"""


from injector import inject
from lostservice.configuration import Configuration
from lostservice.exception import LoopException
from lostservice.model.responses import ResponseMapping, ListServicesByLocationResponse
import lostservice.geometry as geom
from lostservice.db.gisdb import GisDbInterface

import json
from lostservice.model.geodetic import Point
from lostservice.model.geodetic import Circle
from lostservice.model.geodetic import Ellipse
from lostservice.model.geodetic import Polygon as geodetic_polygon
from lostservice.model.geodetic import Arcband

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

    def list_services_by_location_for_point(self, service, location):
        """
        List services for the given point.

        :param service: The identifier for the service to look up.
        :type service: ``str``
        :param location: location object.
        :type location: `location object`
        :param return_shape: Whether or not to return the geometries of found mappings.
        :type return_shape: ``bool``
        :return: The service mappings for the given point.
        :rtype: ``list`` of ``dict``
        """
        if service is not None:
            esb_table = [self._mappings[key] for key in self._mappings if service + '.' in key]
            result = self._db_wrapper.get_list_services_for_point(location, esb_table)
            results = [i[0].get('serviceurn') for i in result if i and i[0].get('serviceurn')]
            return results
        elif service is None:
            esb_table = [self._mappings[key] for key in self._mappings if not '.' in key]
            result = self._db_wrapper.get_list_services_for_point(location, esb_table)
            results = [i[0].get('serviceurn') for i in result if i and i[0].get('serviceurn')]
            return results

    def list_services_by_location_for_civicaddress(self, civic_request):
        from civvy.db.postgis.locating.streets import PgStreetsAggregateLocatorStrategy
        from civvy.db.postgis.locating.points import PgPointsAggregateLocatorStrategy
        from civvy.locating import CivicAddress, CivicAddressSourceMapCollection, Locator
        from civvy.db.postgis.query import PgQueryExecutor

        # The locator needs some information about the underlying data store.
        jsons = json.dumps(self._list_service_config.settings_for_service("civvy_map"))

        # From the JSON configuration, create the source maps that apply to this database.
        source_maps = CivicAddressSourceMapCollection(config=jsons)

        civvy_obj = civic_request.location.location

        # Create the query executor for the PostgreSQL database.
        host = self._list_service_config._config.get('Database', 'host', as_object=False, required=True)
        db_name = self._list_service_config._config.get('Database', 'dbname', as_object=False, required=True)
        username = self._list_service_config._config.get('Database', 'username', as_object=False, required=True)
        password = self._list_service_config._config.get('Database', 'password', as_object=False, required=True)
        query_executor = PgQueryExecutor(database=db_name, host=host, user=username, password=password)

        # Now let's create the locator and supply it with the common default strategies.
        locator = Locator(strategies=[
            PgPointsAggregateLocatorStrategy(query_executor=query_executor),
            PgStreetsAggregateLocatorStrategy(query_executor=query_executor)
        ], source_maps=source_maps)

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
            civic_dict['a6'] = civvy_obj.rd
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

        # We can create several civic addresses and pass them to the locator.
        civic_address = CivicAddress(**civic_dict)

        # Let's get the results for this civic address.
        locator_results = locator.locate_civic_address(civic_address=civic_address)
        mappings = None
        if len(locator_results) > 0:
            first_civic_point = None
            for locater_result in locator_results:
                if locater_result.score==0:
                    first_civic_point = locater_result
                    break
            if first_civic_point:
                civvy_geometry = first_civic_point.geometry
                spatial_reference = civvy_geometry.GetSpatialReference()
                epsg = spatial_reference.GetAttrValue("AUTHORITY", 0)
                srid = spatial_reference.GetAttrValue("AUTHORITY", 1)
                spatial_ref = "{0}::{1}".format(epsg, srid)
                point = Point()
                point.latitude = civvy_geometry.GetY()
                point.longitude = civvy_geometry.GetX()
                point.spatial_ref = spatial_ref
                mappings = self.list_services_by_location_for_point(
                    civic_request.service,
                    point)

        return mappings

    def list_services_by_location_for_circle(self, service, location):
        """
        List services for the given circle.

        :param service: The identifier for the service to look up.
        :type service: ``str``
        :param location: location object.
        :type location: `location object`
        :param return_shape: Whether or not to return the geometries of found mappings.
        :type return_shape: ``bool``
        :return: The service mappings for the given circle.
        :rtype: ``list`` of ``dict``
        """
        if service is not None:
            esb_table = [self._mappings[key] for key in self._mappings if service + '.' in key]
            result = self._db_wrapper.get_intersecting_list_service_for_circle(location, esb_table)
            results = [i[0].get('serviceurn') for i in result if i and i[0].get('serviceurn')]
            return results
        elif service is None:
            esb_table = [self._mappings[key] for key in self._mappings if not '.' in key]
            result = self._db_wrapper.get_intersecting_list_service_for_circle(location, esb_table)
            results = [i[0].get('serviceurn') for i in result if i and i[0].get('serviceurn')]
            return results

    def list_services_by_location_for_ellipse(self, service, location):
        """
        List services for the given ellipse.

        :param service: The identifier for the service to look up.
        :type service: ``str``
        :param location: location object.
        :type location: `location object`
        :param boundary_table: The name of the service boundary table.
        :type boundary_table: `str``
        :return: The service mappings for the given ellipse.
        :rtype: ``list`` of ``dict``
        """
        if service is not None:
            esb_table = [self._mappings[key] for key in self._mappings if service + '.' in key]
            result = self._db_wrapper.get_list_services_for_ellipse(location, esb_table)
            results = [i[0].get('serviceurn') for i in result if i and i[0].get('serviceurn')]
            return results
        elif service is None:
            esb_table = [self._mappings[key] for key in self._mappings if not '.' in key]
            result = self._db_wrapper.get_list_services_for_ellipse(location, esb_table)
            results = [i[0].get('serviceurn') for i in result if i and i[0].get('serviceurn')]
            return results

    def list_service_by_location_for_arcband(self, service, location, return_shape=False):
        """
        List services for the given arcband.

        :param service: The identifier for the service to look up.
        :type service: ``str``
        :param location: location object.
        :type location: `location object`
        :param return_shape: Whether or not to return the geometries of found mappings.
        :type return_shape: ``bool``
        :return: The service mappings for the given arcband.
        :rtype: ``list`` of ``dict``
        """
        arcband = geom.generate_arcband(location.longitude,
                                        location.latitude,
                                        location.spatial_ref,
                                        location.start_angle,
                                        location.opening_angle,
                                        location.inner_radius,
                                        location.outer_radius)
        points = geom.get_vertices_for_geom(arcband)[0]
        polygon = geodetic_polygon()
        polygon.vertices = points
        polygon.spatial_ref = location.spatial_ref
        return self.list_services_by_location_for_polygon(service, polygon, return_shape)

    def list_services_by_location_for_polygon(self, service, location, return_shape=False):
        """
        Listservices for the given polygon.

        :param service_urn: The identifier for the service to look up.
        :type service_urn: ``str``
        :param location: location object.
        :type location: `location object`
        :param return_shape: Whether or not to return the geometries of found mappings.
        :type return_shape: ``bool``
        :return: The service mappings for the given polygon.
        :rtype: ``list`` of ``dict``
        """
        if service is not None:
            esb_table = [self._mappings[key] for key in self._mappings if service + '.' in key]
            result = self._db_wrapper.get_intersecting_list_service_for_polygon(location, esb_table)
            results = [i[0].get('serviceurn') for i in result if i and i[0].get('serviceurn')]
            return results
        elif service is None:
            esb_table = [self._mappings[key] for key in self._mappings if not '.' in key]
            result = self._db_wrapper.get_intersecting_list_service_for_polygon(location, esb_table)
            results = [i[0].get('serviceurn') for i in result if i and i[0].get('serviceurn')]
            return results


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
    def _check_is_loopback(self, path):
        if self._list_service_config.source_uri() in path:
            raise LoopException("LoopError")

    def list_services_by_location_for_point(self, request):
        """
        List service for a point.

        :param request:  A ListService request object with a point location.
        :type request :py:class:`lostservice.model.requests.ListServiceRequest`
        :return: A ListService response.
        :rtype: :py:class:`lostservice.model.responses.ListServiceResponse`
        """
        self._check_is_loopback(request.path)
        mappings = self._inner.list_services_by_location_for_point(
            request.service,
            request.location.location
        )
        return self._build_response(request.path, request.location.id, mappings, request.nonlostdata)

    def list_services_by_location_for_civicaddress(self, request):
        """

        :param request:
        :return:
        """
        self._check_is_loopback(request.path)
        mappings = self._inner.list_services_by_location_for_civicaddress(request)
        return self._build_response(request.path, request.location.id, mappings, request.nonlostdata)

    def list_services_by_location_for_circle(self, request):
        """
        List service for a circle.

        :param request:  A ListService request object with a circle location.
        :type request :py:class:`lostservice.model.requests.ListServiceRequest`
        :return: A ListService response.
        :rtype: :py:class:`lostservice.model.responses.ListServiceResponse`
        """
        self._check_is_loopback(request.path)
        mappings = self._inner.list_services_by_location_for_circle(
            request.service,
            request.location.location)
        return self._build_response(request.path, request.location.id, mappings, request.nonlostdata)

    def list_services_by_location_for_ellipse(self, request):
        """
        List service for an ellipse.

        :param request:  A ListService request object with a point location.
        :type request :py:class:`lostservice.model.requests.ListServiceRequest`
        :return: A ListService response.
        :rtype: :py:class:`lostservice.model.responses.ListServiceResponse`
        """
        self._check_is_loopback(request.path)
        mappings = self._inner.list_services_by_location_for_ellipse(
            request.service,
            request.location.location)
        return self._build_response(request.path, request.location.id, mappings, request.nonlostdata)

    def list_service_by_location_for_arcband(self, request):
        """
        List service for an arcband.

        :param request:  A ListService request object with a point location.
        :type request :py:class:`lostservice.model.requests.ListServiceRequest`
        :return: A ListService response.
        :rtype: :py:class:`lostservice.model.responses.ListServiceResponse`
        """
        self._check_is_loopback(request.path)
        mappings = self._inner.list_service_by_location_for_arcband(
            request.service,
            request.location.location)
        return self._build_response(request.path, request.location.id, mappings, request.nonlostdata)

    def list_services_by_location_for_polygon(self, request):
        """
        List service for an arcband.

        :param request:  A ListService request object with a point location.
        :type request :py:class:`lostservice.model.requests.ListServiceRequest`
        :return: A ListService response.
        :rtype: :py:class:`lostservice.model.responses.ListServiceResponse`
        """
        self._check_is_loopback(request.path)
        mappings = self._inner.list_services_by_location_for_polygon(
            request.service,
            request.location.location
        )
        return self._build_response(request.path, request.location.id, mappings, request.nonlostdata)

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
        resp_mapping.source_id = mapping['srcunqid']
        resp_mapping.service_urn = mapping['serviceurn']
        resp_mapping.last_updated = mapping['updatedate']
        return resp_mapping
