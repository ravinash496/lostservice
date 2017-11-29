#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. currentmodule:: lostservice.handling.core
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

Core handler implementation classes.
"""

from injector import inject
import lostservice.model.responses as responses
from lostservice.configuration import Configuration
from lostservice.db.gisdb import GisDbInterface
from lostservice.exception import BadRequestException
from lostservice.handler import Handler
from lostservice.handling.findservice import FindServiceOuter
from lostservice.handling.findservice import FindServiceInner
from lostservice.handling.listServicesByLocation import ListServiceBylocationOuter
from lostservice.model.geodetic import Arcband
from lostservice.model.geodetic import Circle
from lostservice.model.geodetic import Ellipse
from lostservice.model.geodetic import Point
from lostservice.model.geodetic import Polygon
from lostservice.model.civic import CivicAddress
import lostservice.coverage.resolver as cov
from lostservice.configuration import general_logger
from lostservice.exception import NotFoundException
import lostservice.defaultroutes.defaultroutehandler as def_routes

logger = general_logger()


class ListServicesHandler(Handler):
    """
    Base listServices request handler.
    """
    @inject
    def __init__(self, config: Configuration, db_wrapper: GisDbInterface):
        """
        Constructor

        :param config: The configuration
        :type config: :py:class:`lostservice.configuration.Configuration`
        :param db_wrapper: The db wrapper class instance.
        :type db_wrapper: :py:class:`lostservice.db.gisdb.GisDbInterface`
        """
        super(ListServicesHandler, self).__init__(config, db_wrapper)

    def handle_request(self, request, context):
        """
        Entry point for request handling.

        :param request: The request
        :type request: A subclass of :py:class:`ListServicesRequest`
        :param context: The request context.
        :type context: ``dict``
        :return: The response.
        :rtype: :py:class:`ListServicesResponse`
        """

        mappings = self._db_wrapper.get_urn_table_mappings()

        service_list = mappings.keys()
        if request.service:
            # Filter the response to only those that are sub-services of the given
            # service urn
            root_service = request.service + '.'
            filtered = filter(lambda s: root_service in s, service_list)
            service_list = filtered
        else:
            # Filter the response to only the Top Level Services
            filtered= filter(lambda k: '.' not in k, service_list)
            service_list = filtered

        # No Recursion available so just add our path
        our_path = self._config.get('Service', 'source_uri', as_object=False, required=False)

        # Add our LVF/ECRF path to any other paths aready in the original request (recursive)
        request.path.append(our_path)
        response = responses.ListServicesResponse(service_list, request.path, request.nonlostdata)

        return response


class FindServiceHandler(Handler):
    """
    Base findService request handler.
    """

    @inject
    def __init__(self, outer: FindServiceOuter, cov_resolver: cov.CoverageResolverWrapper, default_route_handler: def_routes.DefaultRouteHandler):
        """
        Constructor

        :param outer: An instance of the outer find service class.
        :type config: :py:class:`lostservice.handling.findservice.FindServiceOuter`
        :param db_wrapper: The db wrapper class instance.
        :type db_wrapper: :py:class:`lostservice.db.gisdb.GisDbInterface`
        """
        # TODO - clean this up since handlers shouldn't have direct references to config or the db any more.
        super(FindServiceHandler, self).__init__(None, None, cov_resolver=cov_resolver)
        self._outer = outer
        self._default_route_handler = default_route_handler

    def handle_request(self, request, context):

        """
        Entry point for request handling.

        :param request: The request
        :type request: A subclass of :py:class:`FindServiceRequest`
        :param context: The request context.
        :type context: ``dict``
        :return: The response.
        :rtype: :py:class:`FindServiceResponse`
        """

        try:
            self.check_coverage(request.location.location)
        except Exception:
            raise

        try:
            response = None
            if type(request.location.location) is Point:
                response = self._outer.find_service_for_point(request)
            elif type(request.location.location) is Circle:
                response = self._outer.find_service_for_circle(request)
            elif type(request.location.location) is Ellipse:
                response = self._outer.find_service_for_ellipse(request)
            elif type(request.location.location) is Arcband:
                response = self._outer.find_service_for_arcband(request)
            elif type(request.location.location) is Polygon:
                response = self._outer.find_service_for_polygon(request)
            elif type(request.location.location) is CivicAddress:
                response = self._outer.find_service_for_civicaddress(request)
            else:
                logger.error('Invalid location type.')
                raise BadRequestException('Invalid location type.')
        except NotFoundException:
            if type(request.location.location) is CivicAddress:
                # check if default route exists, if not raise the same exception
                mapping = self._default_route_handler.check_default_route(request)
                # build the response with this mapping
                response = self._outer._build_response(request.path, request.location.id, mapping, request.nonlostdata)
            else:
                raise

        if response.mappings is None or len(response.mappings) == 0:
            mapping = self._default_route_handler.check_default_route(request)
            # build the response with this mapping
            response = self._outer._build_response(request.path, request.location.id, mapping, request.nonlostdata)

        return response


class GetServiceBoundaryHandler(Handler):
    """
    Base getServiceBoundary request handler.
    """
    @inject
    def __init__(self, config: Configuration, db_wrapper: GisDbInterface, inner: FindServiceInner):
        """
        Constructor

        :param config: The configuration
        :type config: :py:class:`lostservice.configuration.Configuration`
        :param db_wrapper: The db wrapper class instance.
        :type db_wrapper: :py:class:`lostservice.db.gisdb.GisDbInterface`
        :param inner: The FindService inner class instance
        :type inner: :py:class:lostservice.handling.FindServiceInner'
        """
        super(GetServiceBoundaryHandler, self).__init__(config, db_wrapper)
        self._inner = inner

    def handle_request(self, request, context):
        """
        Entry point for request handling.

        :param request: The request
        :type request: A subclass of :py:class:`GetServiceBoundaryRequest`
        :param context: The request context.
        :type context: ``dict``
        :return: The response.
        :rtype: :py:class:`GetServiceBoundaryResponse`
        """
        # Get the table mappings, this should come from cache eventually.
        mappings = self._db_wrapper.get_urn_table_mappings()

        # loop through all the tables to find the id until its found.
        for urn_mapping in mappings.keys():
            esb_table = mappings[urn_mapping]
            results = self._db_wrapper.get_boundaries_for_previous_id(request.key, esb_table)
            if results:
                # No Recursion available so just add our path
                our_path = self._config.get('Service', 'source_uri', as_object=False, required=False)
                # Add our LVF/ECRF path to any other paths aready in the original request (recursive)
                results[0]['path'] = our_path

                # Add NonLoSTdata items
                results[0]['nonlostdata'] = request.nonlostdata

                break
        for item in results:
            item =  self._inner.apply_service_boundary_policy(item, True)

        return results


class ListServicesByLocationHandler(Handler):
    """
    Base ListService request handler.
    """

    @inject
    def __init__(self, outer: ListServiceBylocationOuter, cov_resolver: cov.CoverageResolverWrapper):
        """
        Constructor

        :param outer: An instance of the outer List service class.
        :type config: :py:class:`lostservice.handling.Listservice.ListServiceOuter`
        :param db_wrapper: The db wrapper class instance.
        :type db_wrapper: :py:class:`lostservice.db.gisdb.GisDbInterface`
        """
        # TODO - clean this up since handlers shouldn't have direct references to config or the db any more.
        super(ListServicesByLocationHandler, self).__init__(None, None, cov_resolver=cov_resolver)
        self._outer = outer

    def handle_request(self, request, context):

        """
        Entry point for request handling.

        :param request: The request
        :type request: A subclass of :py:class:`ListServicesByLocationRequest`
        :param context: The request context.
        :type context: ``dict``
        :return: The response.
        :rtype: :py:class:`ListServicesByLocationResponse`
        """
        try:
            self.check_coverage(request.location.location)
        except Exception:
            raise

        response = None
        if type(request.location.location) is Point:
            response = self._outer.list_services_by_location_for_point(request)
        elif type(request.location.location) is Circle:
            response = self._outer.list_services_by_location_for_circle(request)
        elif type(request.location.location) is Ellipse:
            response = self._outer.list_services_by_location_for_ellipse(request)
        elif type(request.location.location) is Arcband:
            response = self._outer.list_service_by_location_for_arcband(request)
        elif type(request.location.location) is Polygon:
            response = self._outer.list_services_by_location_for_polygon(request)
        elif type(request.location.location) is CivicAddress:
            response = self._outer.list_services_by_location_for_civicaddress(request)
        else:
            logger.error('Invalid location type.')
            raise BadRequestException('Invalid location type.')

        return response
