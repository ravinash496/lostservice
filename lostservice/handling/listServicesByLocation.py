#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. currentmodule:: lostservice.handling.Listservice
.. moduleauthor:: Avinash <arayapudi@geo-comm.com>

Implementation classes for Listservice queries.
"""


from injector import inject
from lostservice.configuration import Configuration
from lostservice.exception import LoopException, NotFoundException
from lostservice.model.responses import ResponseMapping, ListServicesByLocationResponse
import lostservice.geometry as geom
from lostservice.db.gisdb import GisDbInterface

import json
from lostservice.model.geodetic import Point
from lostservice.model.geodetic import Circle
from lostservice.model.geodetic import Ellipse
from lostservice.model.geodetic import Polygon as geodetic_polygon
from lostservice.model.geodetic import Arcband
from lostservice.configuration import general_logger
from civvy.db.postgis.locating.streets import PgStreetsAggregateLocatorStrategy
from civvy.db.postgis.locating.points import PgPointsAggregateLocatorStrategy
from civvy.locating import CivicAddress, CivicAddressSourceMapCollection, Locator
from civvy.db.postgis.query import PgQueryExecutor

logger = general_logger()


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
    def __init__(self, config: ListServiceBYLocationConfigWrapper, db_wrapper: GisDbInterface,
                 query_executor: PgQueryExecutor = None):
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
        self._query_executor = query_executor

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
            logger.debug('Running civic address query for list services through civvy.')
            locator_results = locator.locate_civic_address(civic_address=civic_address, offset_distance=offset_distance)

            return locator_results
        else:
            # Who did this, and why are you doing it?!
            logger.error('Locator object not passed.')
            raise NotFoundException('Locator not defined, cannot complete civic address request.', None)
            return None

    def list_services_by_location_for_civicaddress(self, civic_request):
        """
        Function to find the service for the civic address

         :param civic_request: civic address request
         :type civic_request: :py:class:`lostservice.model.requests.ListServicesRequest`
         :return: The service mappings for the given civic address.
        """
        rcl_offset_distance = self._list_service_config.get('Policy', 'offset_distance_from_centerline',
                                                            as_object=False,
                                                            required=False)
        # Now let's create the locator and supply it with the common default strategies.
        locator = self.get_civvy_locator(rcl_offset_distance)
        # Let's get the results for this civic address.
        locator_results = self.run_civic_location_search(locator=locator,
                                                         offset_distance=rcl_offset_distance,
                                                         civic_request=civic_request)
        mappings = None
        point = Point()
        if len(locator_results) > 0:
            first_civic_point = None
            for locator_result in locator_results:
                if locator_result.score == 0:
                    first_civic_point = locator_result
                    break
            if first_civic_point:
                civvy_geometry = first_civic_point.geometry
                spatial_reference = civvy_geometry.GetSpatialReference()
                epsg = spatial_reference.GetAttrValue("AUTHORITY", 0)
                srid = spatial_reference.GetAttrValue("AUTHORITY", 1)
                spatial_ref = "{0}::{1}".format(epsg, srid)
                point.latitude = civvy_geometry.GetY()
                point.longitude = civvy_geometry.GetX()
                point.spatial_ref = spatial_ref
                mappings = self.list_services_by_location_for_point(
                    civic_request.service,
                    point)
        return {'mappings': mappings,
                'latitude': point.latitude,
                'longitude': point.longitude}

    def list_services_by_location_for_circle(self, service, location):
        """
        List services for the given circle.

        :param service: The identifier for the service to look up.
        :type service: ``str``
        :param location: location object.
        :type location: `location object`
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
        return_value = {'latitude': request.location.location.latitude,
                        'longitude': request.location.location.longitude,
                        'response': self._build_response(request.path,
                                                         request.location.id,
                                                         mappings,
                                                         request.nonlostdata)}
        return return_value

    def list_services_by_location_for_civicaddress(self, request):
        """

        :param request:
        :return:
        """
        self._check_is_loopback(request.path)
        inner_result = self._inner.list_services_by_location_for_civicaddress(request)
        return_value = {'latitude': inner_result['latitude'],
                        'longitude': inner_result['longitude'],
                        'response': self._build_response(request.path,
                                                         request.location.id,
                                                         inner_result['mappings'],
                                                         request.nonlostdata)}

        return return_value

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

        return_value = {'latitude': request.location.location.latitude,
                        'longitude': request.location.location.longitude,
                        'response': self._build_response(request.path,
                                                         request.location.id,
                                                         mappings,
                                                         request.nonlostdata)}
        return return_value

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
        return_value = {'latitude': request.location.location.latitude,
                        'longitude': request.location.location.longitude,
                        'response': self._build_response(request.path,
                                                         request.location.id,
                                                         mappings,
                                                         request.nonlostdata)}
        return return_value

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
        return_value = {}
        try:
            lat = request.location.location.build_shapely_geometry().representative_point().y
            long = request.location.location.build_shapely_geometry().representative_point().x
            resp = self._build_response(request.path, request.location.id, mappings, request.nonlostdata)
            return_value = {'latitude': lat,
                            'longitude': long,
                            'response': resp}
        except Exception as e:
            logger.error(e)

        return return_value

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
            request.location.location)
        return_value = {}
        try:
            lat = request.location.location.build_shapely_geometry().centroid.y
            long = request.location.location.build_shapely_geometry().centroid.x
            resp = self._build_response(request.path, request.location.id, mappings, request.nonlostdata)

            return_value = {'latitude': lat,
                            'longitude': long,
                            'response': resp}
        except Exception as e:
            logger.error(e)

        return return_value

    def _build_response(self, path, location_id, mapping, nonlostdata):
        """
        Builds a List service response.

        :param path: The list of path elements that came in with the request.
        :type path: ``list`` of ``str``
        :param location_id: The location id that came in with the request.
        :type location_id: ``str``
        :param mapping: A list of all mappings returned by the query.
        :type mapping: ``list`` of ``dict``
        :param nonlostdata: Pass through elements from the request.
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

        :param mapping: A dictionary of the query result attributes for a mapping.
        :type mapping: ``dict``
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
