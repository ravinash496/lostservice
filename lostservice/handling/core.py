#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. currentmodule:: lostservice.handling.core
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

Core handler implementation classes.
"""

from sqlalchemy import create_engine
import datetime
import pytz

from lostservice.db.utilities import get_urn_table_mappings
from lostservice.db.utilities import apply_policy_settings
from lostservice.handler import Handler
import lostservice.model.responses as responses
import lostservice.db.spatial as spatial
from lostservice.model.location import Circle
from lostservice.model.location import Point
from lostservice.context import ServiceExpiresPolicyEnum
from lostservice.context import PolygonMultipleMatchPolicyEnum

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

        # Get the table mappings, this should come from cache eventually.
        mappings = get_urn_table_mappings(engine)

        # From the mappings, look up the table name from the incoming service urn.
        esb_table = mappings[request.service]

        if type(request.location.location) is Circle:

            polygon_multiple_match_policy = context.configuration.get('Policy', 'polygon_multiple_match_policy',
                                                                      as_object=False, required=False)
            return_area = False
            if polygon_multiple_match_policy == PolygonMultipleMatchPolicyEnum.ReturnAreaMajority.name:
                return_area = True

            results = spatial.get_intersecting_boundaries_for_circle(request.location.location.longitude,
                                                                     request.location.location.latitude,
                                                                     request.location.location.spatial_ref,
                                                                     float(request.location.location.radius),
                                                                     request.location.location.uom, esb_table, engine,
                                                                     return_area)
        elif type(request.location.location) is Point:
            results = spatial.get_containing_boundary_for_point(
                request.location.location.longitude,
                request.location.location.latitude,
                request.location.location.spatial_ref,
                esb_table, engine)

        results = apply_policy_settings(context, results, request)
        # Create a list to contain mutiple response mappings
        response_mapping_list = []

        for row in results:
            response_mapping = {}   #TODO How to deal with None?

            response_mapping['displayname'] = row['displayname']
            response_mapping['serviceurn'] = row['serviceurn']
            response_mapping['routeuri'] = row['routeuri']
            response_mapping['servicenum'] = row['servicenum']
            response_mapping['mapping_sourceid'] = row['gcunqid']

            response_mapping['mapping_lastupdate'] = None
            lastupdatefield = context.configuration.get('Service', 'last_update_field', as_object=False, required=False)
            if lastupdatefield is not None:
                response_mapping['mapping_lastupdate'] = row[lastupdatefield]

            path = context.configuration.get('Service', 'source_uri', as_object=False, required=False)
            response_mapping['path'] = [path]

            response_mapping['mapping_source'] = context.configuration.get('Service', 'source_uri', as_object=False, required=False)

            #Get the entire dictionary of settings for this service
            service_settings_dict = context.configuration.get('Service', esb_table, as_object=True, required=False)
            if service_settings_dict == None:
                # Config not set for specific table use default Service Values
                service_settings_dict = context.configuration.get('Service', 'default', as_object=True, required=False)
                print("[Service] settings for %s not found. [Service] default settings applied." % esb_table)

            mapping_service_expires_policy = service_settings_dict['service_expire_policy']
            mapping_service_expires_timespan = service_settings_dict['service_expire_policy']

            # Based on setting Set Expires to: currentTime + TimeSpan setting or "NO-CACHE" or "NO-EXPIRATION"
            if mapping_service_expires_policy == ServiceExpiresPolicyEnum.TimeSpan.name:
                # Expected to be in UTC format plus timespan (minutes) interval setting 2010-05-18T16:47:55.9620000-06:00
                mapping_expires = datetime.datetime.now(tz=pytz.utc) + datetime.timedelta(minutes=int(mapping_service_expires_timespan))
                response_mapping['mapping_expires'] = mapping_expires.isoformat()
            elif mapping_service_expires_policy == ServiceExpiresPolicyEnum.NoCache.name:
                response_mapping['mapping_expires'] = 'NO-CACHE'
            elif mapping_service_expires_policy == ServiceExpiresPolicyEnum.NoExpiration.name:
                response_mapping['mapping_expires'] = 'NO-EXPIRATION'


            # The location used in the request (Optional). Get this from the request location's id.
            response_mapping['locationUsed'] = [request.location.id]

            response_mapping_list.append(response_mapping)

        # End of For

        return response_mapping_list







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




