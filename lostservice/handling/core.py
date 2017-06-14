#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. currentmodule:: lostservice.handling.core
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

Core handler implementation classes.
"""


import datetime
import pytz
from injector import inject
from lostservice.configuration import Configuration
from lostservice.db.gisdb import GisDbInterface
from lostservice.handler import Handler
import lostservice.model.responses as responses
from lostservice.model.location import Circle
from lostservice.model.location import Point
from lostservice.configuration import ServiceExpiresPolicyEnum


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

        path = self._config.get('Service', 'source_uri', as_object=False, required=False)
        response = responses.ListServicesResponse(service_list, [path])

        return response


class FindServiceHandler(Handler):
    """
    Base findService request handler.
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
        super(FindServiceHandler, self).__init__(config, db_wrapper)

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

        # Get the table mappings, this should come from cache eventually.
        mappings = self._db_wrapper.get_urn_table_mappings()

        # From the mappings, look up the table name from the incoming service urn.
        esb_table = mappings[request.service]

        if type(request.location.location) is Circle:
            results = self._db_wrapper.get_intersecting_boundaries_for_circle(
                request.location.location.longitude,
                request.location.location.latitude,
                request.location.location.spatial_ref,
                float(request.location.location.radius),
                request.location.location.uom, esb_table)

        elif type(request.location.location) is Point:
            results = self._db_wrapper.get_containing_boundary_for_point(
                request.location.location.longitude,
                request.location.location.latitude,
                request.location.location.spatial_ref,
                esb_table)

        for row in results:
            displayname = row['displayname']
            serviceurn = row['serviceurn']
            routeuri = row['routeuri']
            servicenum = row['servicenum']
            mapping_sourceid = row['gcunqid']

            # Is this config setting necessary? All UDM tables have this and it is well known.
            mapping_lastupdate = None
            lastupdatefield = self._config.get('Service', 'last_update_field', as_object=False, required=False)
            if lastupdatefield is not None:
                mapping_lastupdate = row[lastupdatefield]

        path = self._config.get('Service', 'source_uri', as_object=False, required=False)
        mapping_source = self._config.get('Service', 'source_uri', as_object=False, required=False)
        mapping_service_expires_policy = self._config.get('Service', 'service_expires_policy', as_object=False, required=False)
        mapping_service_expires_timespan = self._config.get('Service', 'service_expires_timespan', as_object=False, required=False)

        # Based on setting Set Expires to: currentTime + TimeSpan setting or "NO-CACHE" or "NO-EXPIRATION"
        if mapping_service_expires_policy == ServiceExpiresPolicyEnum.TimeSpan.name:
            # Expected to be in UTC format plus timespan (minutes) interval setting 2010-05-18T16:47:55.9620000-06:00
            mapping_expires = datetime.datetime.now(tz=pytz.utc) + datetime.timedelta(minutes=int(mapping_service_expires_timespan))
        elif mapping_service_expires_policy == ServiceExpiresPolicyEnum.NoCache.name:
            mapping_expires = 'NO-CACHE'
        elif mapping_service_expires_policy == ServiceExpiresPolicyEnum.NoExpiration.name:
            mapping_expires = 'NO-EXPIRATION'

        # The location used in the request (Optional). Get this from the request location's id.
        locationUsed = request.location.id
        value_or_reference = request.serviceBoundary

        response = responses.FindServiceResponse(displayname, serviceurn, routeuri, servicenum, [path], [locationUsed],
                                                 mapping_lastupdate, mapping_source, mapping_sourceid, mapping_expires,
                                                 value_or_reference)
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
        raise NotImplementedError("Can't handle getServiceBoundary requests just yet, come back later.")


class ListServicesByLocationHandler(Handler):
    """
    Base listServicesByLocation request handler.
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
        super(ListServicesByLocationHandler, self).__init__(config, db_wrapper)

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
        raise NotImplementedError("Can't handle getServicesByLocation requests just yet, come back later.")




