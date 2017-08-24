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
from lostservice.handler import Handler
from lostservice.handling.findservice import FindServiceOuter, FindServiceException
from lostservice.handling.listServicesByLocation import ListServiceBylocationOuter, ListServiceBYLocationException
from lostservice.model.location import Arcband
from lostservice.model.location import Circle
from lostservice.model.location import Ellipse
from lostservice.model.location import Point
from lostservice.model.location import Polygon


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
    def __init__(self, outer: FindServiceOuter):
        """
        Constructor

        :param outer: An instance of the outer find service class.
        :type config: :py:class:`lostservice.handling.findservice.FindServiceOuter`
        :param db_wrapper: The db wrapper class instance.
        :type db_wrapper: :py:class:`lostservice.db.gisdb.GisDbInterface`
        """
        # TODO - clean this up since handlers shouldn't have direct references to config or the db any more.
        super(FindServiceHandler, self).__init__(None, None)
        self._outer = outer

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
        else:
            raise FindServiceException('Invalid location type.')

        return response


class GetServiceBoundaryHandler(Handler):
    """
    Base getServiceBoundary request handler.
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
        super(GetServiceBoundaryHandler, self).__init__(config, db_wrapper)

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

        return results


class ListServicesByLocationHandler(Handler):
    """
    Base ListService request handler.
    """

    @inject
    def __init__(self, outer: ListServiceBylocationOuter):
        """
        Constructor

        :param outer: An instance of the outer List service class.
        :type config: :py:class:`lostservice.handling.Listservice.ListServiceOuter`
        :param db_wrapper: The db wrapper class instance.
        :type db_wrapper: :py:class:`lostservice.db.gisdb.GisDbInterface`
        """
        # TODO - clean this up since handlers shouldn't have direct references to config or the db any more.
        super(ListServicesByLocationHandler, self).__init__(None, None)
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
        response = None
        if type(request.location.location) is Point:
            response = self._outer.List_ServiceBylocation_for_point(request)
        elif type(request.location.location) is Circle:
            response = self._outer.List_serviceBylocation_for_circle(request)
        elif type(request.location.location) is Ellipse:
            response = self._outer.List_serviceBylocation_for_ellipse(request)
        elif type(request.location.location) is Arcband:
            response = self._outer.List_serviceBylocation_for_arcband(request)
        elif type(request.location.location) is Polygon:
            response = self._outer.List_serviceBylocation_for_polygon(request)
        else:
            raise ListServiceBYLocationException('Invalid location type.')

        return response
