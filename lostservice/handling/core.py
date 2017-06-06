#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. currentmodule:: lostservice.handling.core
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

Core handler implementation classes.
"""

from sqlalchemy import create_engine

from lostservice.db.postgisqueries import query_for_circle
from lostservice.db.utilities import get_urn_table_mappings
from lostservice.handler import Handler
import lostservice.model.responses as responses
import lostservice.db.spatial as spatial


class ListServicesHandler(Handler):
    """
    Base listServices request handler.
    """

    def __init__(self):
        """
        Constructor
        """
        super(ListServicesHandler, self).__init__()

    def handle_request(self, request, context):
        """
        Entry point for request handling.

        :param request: The request
        :type request: A subclass of :py:class:`ListServicesRequest`
        :param context: The context.
        :type context: :py:class:`lostservice.context.LostContext`
        :return: The response.
        :rtype: A subclass of :py:class:`ListServicesResponse`
        """
        engine = create_engine(context.get_db_connection_string())

        mappings = get_urn_table_mappings(engine)

        service_list = mappings.keys()
        if request.service:
            # Filter the response to only those that are sub-services of the given
            # service urn
            root_service = request.service + '.'
            filtered = filter(lambda s: root_service in s, service_list)
            service_list = filtered


        path = context.configuration.get('Service', 'source_uri', as_object=False, required=False)
        response = responses.ListServicesResponse(service_list, [path])

        return response


class FindServiceHandler(Handler):
    """
    Base findService request handler.
    """

    def __init__(self):
        """
        Constructor
        """
        super(FindServiceHandler, self).__init__()


class FindServiceHandler(Handler):
    """
    Base findService request handler.
    """

    def __init__(self):
        """
        Constructor
        """
        super(FindServiceHandler, self).__init__()

    def handle_request(self, request, context):
        """
             Entry point for request handling.

             :param request: The request
             :type request: A subclass of :py:class:`FindServiceRequest`
             :param context: The context.
             :type context: :py:class:`lostservice.context.LostContext`
             :return: The response.
             :rtype: A subclass of :py:class:`FindServiceResponse`
             """
        engine = create_engine(context.get_db_connection_string())

        mappings = get_urn_table_mappings(engine)

        service_list = mappings.keys()
        if request.service:
            # Filter the response to only those that are sub-services of the given
            # service urn
            root_service = request.service + '.'
            filtered = filter(lambda s: root_service in s, service_list)
            service_list = list(filtered)

        # TODO Get table name for value in root_service

        srid = 0
        intsrid = request._location.geodetic2d.spatial_ref.find("::")
        if intsrid >= 0:
            srid = int(request._location.geodetic2d.spatial_ref[intsrid +2:])
        else:
            srid = 4326

        tablename = "esbpsap"
        results = query_for_circle(request._location.geodetic2d.longitude, request._location.geodetic2d.latitude, srid, float(request._location.geodetic2d.radius), request._location.geodetic2d.uom, tablename, engine)

        for row in results:
            displayname = row['displayname']
            serviceurn = row['serviceurn']
            routeuri = row['routeuri']
            servicenum = row['servicenum']

        results.close()
        path = context.configuration.get('Service', 'source_uri', as_object=False, required=False)

        response = responses.FindServiceResponse(displayname, serviceurn, routeuri, servicenum, [path])
        return response

    def handle_request(self, request, context):
        """
        Entry point for request handling.

        :param request: The request
        :type request: A subclass of :py:class:`FindServiceRequest`
        :return: The response.
        :rtype: A subclass of :py:class:`FindServiceResponse`
        """
        # Create an instane of the SQLAlchemy engine from which connections will be created.
        engine = create_engine(context.get_db_connection_string())

        # Get the table mappings, this should come from cache eventually.
        mappings = get_urn_table_mappings(engine)

        # From the mappings, look up the table name from the incoming service urn.
        esb_table = mappings[request.service]

        result = spatial.get_containing_boundary_for_point(
            request.location.location.longitude,
            request.location.location.latitude,
            request.location.location.spatial_ref,
            esb_table, engine)

        response = responses.FindServiceResponse()

        # TODO - Fill out the FindServiceResponse object with information from the
        # TODO - result above.

        return response


class GetServiceBoundaryHandler(Handler):
    """
    Base getServiceBoundary request handler.
    """

    def __init__(self):
        """
        Constructor
        """
        super(GetServiceBoundaryHandler, self).__init__()

    def handle_request(self, request):
        """
        Entry point for request handling.

        :param request: The request
        :type request: A subclass of :py:class:`GetServiceBoundaryRequest`
        :return: The response.
        :rtype: A subclass of :py:class:`GetServiceBoundaryResponse`
        """
        raise NotImplementedError("Can't handle getServiceBoundary requests just yet, come back later.")


class ListServicesByLocationHandler(Handler):
    """
    Base listServicesByLocation request handler.
    """

    def __init__(self):
        """
        Constructor
        """
        super(ListServicesByLocationHandler, self).__init__()

    def handle_request(self, request, context):
        """
        Entry point for request handling.

        :param request: The request
        :type request: A subclass of :py:class:`ListServicesByLocationRequest`
        :param context: The context.
        :type context: :py:class:`lostservice.context.LostContext`
        :return: The response.
        :rtype: A subclass of :py:class:`ListServicesByLocationResponse`
        """
        raise NotImplementedError("Can't handle getServicesByLocation requests just yet, come back later.")




