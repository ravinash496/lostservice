#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. currentmodule:: lostservice.handling.core
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

Core handler implementation classes.
"""


import datetime
import pytz
from lostservice.db.utilities import apply_policy_settings
from lostservice.db.utilities import case_insensitive_string_to_boolean_conversion
from injector import inject
from lostservice.configuration import Configuration
from lostservice.db.gisdb import GisDbInterface
from lostservice.handler import Handler
import lostservice.model.responses as responses
from lostservice.model.location import Circle
from lostservice.model.location import Ellipse
from lostservice.model.location import Point
from lostservice.model.location import Arcband
from lostservice.configuration import PolygonMultipleMatchPolicyEnum
from lostservice.configuration import PolygonSearchModePolicyEnum
from lostservice.configuration import ServiceExpiresPolicyEnum
import lostservice.geometry as geom
from shapely.geometry import Polygon


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

        # Run spatial query for the specific geometry type
        results = self._process_findservice_geometry(request, esb_table)

        service_boundary_profile = request.location.profile

        results = apply_policy_settings(self._config, results, request)
        # Create a list to contain mutiple response mappings
        response_mapping_list = []

        if results is None:
            return response_mapping_list

        for row in results:

            response_mapping = {}  # TODO How to deal with None?

            response_mapping['displayname'] = row['displayname']
            response_mapping['serviceurn'] = row['serviceurn']
            response_mapping['routeuri'] = row['routeuri']
            response_mapping['servicenum'] = row['servicenum']
            response_mapping['mapping_sourceid'] = row['gcunqid']

            response_mapping['profile'] = service_boundary_profile

            if 'ST_AsGML_1' in row:
                response_mapping['service_gml'] = row['ST_AsGML_1']

            response_mapping['mapping_lastupdate'] = None
            lastupdatefield = 'updatedate'

            if lastupdatefield is not None:
                response_mapping['mapping_lastupdate'] = row[lastupdatefield]

            response_mapping['mapping_source'] = self._config.get('Service', 'source_uri', as_object=False,
                                                                  required=False)

            # Get the entire dictionary of settings for this service
            service_settings_dict = self._config.get('Service', esb_table, as_object=True, required=False)
            if service_settings_dict == None:
                # Config not set for specific table use default Service Values
                service_settings_dict = self._config.get('Service', 'default', as_object=True, required=False)
                print("[Service] settings for %s not found. [Service] default settings applied." % esb_table)

            mapping_service_expires_policy = service_settings_dict['service_expire_policy']
            mapping_service_expires_timespan = service_settings_dict['service_expire_policy']

            # Based on setting Set Expires to: currentTime + TimeSpan setting or "NO-CACHE" or "NO-EXPIRATION"
            if mapping_service_expires_policy == ServiceExpiresPolicyEnum.TimeSpan.name:
                # Expected to be in UTC format plus timespan (minutes) interval setting 2010-05-18T16:47:55.9620000-06:00
                mapping_expires = datetime.datetime.now(tz=pytz.utc) + datetime.timedelta(
                    minutes=int(mapping_service_expires_timespan))
                response_mapping['mapping_expires'] = mapping_expires.isoformat()
            elif mapping_service_expires_policy == ServiceExpiresPolicyEnum.NoCache.name:
                response_mapping['mapping_expires'] = 'NO-CACHE'
            elif mapping_service_expires_policy == ServiceExpiresPolicyEnum.NoExpiration.name:
                response_mapping['mapping_expires'] = 'NO-EXPIRATION'

            # The location used in the request (Optional). Get this from the request location's id.
            response_mapping['locationUsed'] = [request.location.id]
            response_mapping['value_or_reference'] = request.serviceBoundary

            response_mapping_list.append(response_mapping)

        # End of For


        if len(response_mapping_list) > 0:
            # Add Path(s) to any already found in request - recursion is possible
            our_path = self._config.get('Service', 'source_uri', as_object=False, required=False)

            # Add our LVF/ECRF path to any other paths aready in the original request (recursive)
            response_mapping_list[0]['path'] = request.path + [our_path]

            # Add NonLoSTdata items
            response_mapping_list[0]['nonlostdata'] = request.nonlostdata

        return response_mapping_list



    def _process_findservice_geometry(self, request, esb_table):
        """
        Identify and process each type of shape
        :param request: 
        :param esb_table: 
        :return: 
        """

        # TODO remove, now in config wrapper
        proximity_search_policy_string = self._config.get('Policy',
                                                                    'service_boundary_proximity_search_policy',
                                                                    as_object=False, required=False)
        service_boundary_proximity_search_policy = case_insensitive_string_to_boolean_conversion(proximity_search_policy_string)


        if type(request.location.location) is Circle:

            # TODO remove, now in config wrapper
            polygon_multiple_match_policy = self._config.get('Policy', 'polygon_multiple_match_policy',
                                                             as_object=False, required=False)
            return_area = False
            if polygon_multiple_match_policy == PolygonMultipleMatchPolicyEnum.ReturnAreaMajority.name:
                return_area = True

            return_shape = False
            if request.serviceBoundary == 'value':
                return_shape = True

            results = self._db_wrapper.get_intersecting_boundaries_for_circle(
                request.location.location.longitude,
                request.location.location.latitude,
                request.location.location.spatial_ref,
                float(request.location.location.radius),
                request.location.location.uom, esb_table, return_area, return_shape)

            if results is None and service_boundary_proximity_search_policy is True:
                # No results and Policy says we should buffer and research

                # TODO remove, now in config wrapper
                service_boundary_proximity_buffer = self._config.get('Policy',
                                                                     'service_boundary_proximity_buffer',
                                                                     as_object=False, required=False)

                results = self._db_wrapper.get_intersecting_boundaries_for_circle(
                    request.location.location.longitude,
                    request.location.location.latitude,
                    request.location.location.spatial_ref,
                    float(request.location.location.radius),
                    request.location.location.uom, esb_table, return_area, return_shape,
                    service_boundary_proximity_search_policy, service_boundary_proximity_buffer)


        elif type(request.location.location) is Ellipse:

            results = self._db_wrapper.get_intersecting_boundary_for_ellipse(
                request.location.location.longitude,
                request.location.location.latitude,
                request.location.location.spatial_ref,
                float(request.location.location.semiMajorAxis),
                float(request.location.location.semiMinorAxis),
                float(request.location.location.orientation),
                esb_table)

            if results is None and service_boundary_proximity_search_policy is True:
                # No results and Policy says we should buffer and research
                # TODO remove, now in config wrapper
                service_boundary_proximity_buffer = self._config.get('Policy',
                                                                     'service_boundary_proximity_buffer',
                                                                     as_object=False, required=False)
                results = self._db_wrapper.get_intersecting_boundary_for_ellipse(
                    request.location.location.longitude,
                    request.location.location.latitude,
                    request.location.location.spatial_ref,
                    float(request.location.location.semiMajorAxis) + int(service_boundary_proximity_buffer),
                    float(request.location.location.semiMinorAxis) + int(service_boundary_proximity_buffer),
                    float(request.location.location.orientation),
                    esb_table)


        elif type(request.location.location) is Point:
            results = self._db_wrapper.get_containing_boundary_for_point(
                request.location.location.longitude,
                request.location.location.latitude,
                request.location.location.spatial_ref,
                esb_table)

            if results is None and service_boundary_proximity_search_policy is True:
                # No results and Policy says we should buffer and research
                # Create a Circle
                # TODO remove, now in config wrapper
                service_boundary_proximity_buffer = self._config.get('Policy',
                                                                     'service_boundary_proximity_buffer',
                                                                     as_object=False, required=False)
                # TODO remove, now in config wrapper
                polygon_multiple_match_policy = self._config.get('Policy', 'polygon_multiple_match_policy',
                                                                 as_object=False, required=False)
                return_area = False
                if polygon_multiple_match_policy == PolygonMultipleMatchPolicyEnum.ReturnAreaMajority.name:
                    return_area = True

                return_shape = False
                if request.serviceBoundary == 'value':
                    return_shape = True

                results = self._db_wrapper.get_intersecting_boundaries_for_circle(
                    request.location.location.longitude,
                    request.location.location.latitude,
                    request.location.location.spatial_ref,
                    float(service_boundary_proximity_buffer),
                    None, esb_table, return_area, return_shape)

        elif type(request.location.location) is Arcband:
            geom_model = request.location.location
            arcband = geom.generate_arcband(
                geom_model.longitude,
                geom_model.latitude,
                geom_model.start_angle,
                geom_model.opening_angle,
                geom_model.inner_radius,
                geom_model.outer_radius
            )

            points = geom.get_vertices_for_geom(arcband)[0]

            results = self._db_wrapper.get_containing_boundary_for_polygon(
                points,
                geom_model.spatial_ref,
                esb_table
            )


        else:
            # TODO remove, now in config wrapper
            polygon_search_mode_policy = self._config.get('Policy', 'polygon_search_mode_policy',
                                                    as_object=False, required=False)
            if (polygon_search_mode_policy == PolygonSearchModePolicyEnum.SearchUsingCentroid.name):
                #Search using polygon centroid
                # Calculate the centroid using shapely
                ref_polygon = Polygon(request.location.location.get("vertices"))
                pt_array = ref_polygon.centroid       # TODO should this be representative_point() instead?

                # Make sure we found a centroid
                if pt_array is None:
                    return None

                results = self._db_wrapper.get_containing_boundary_for_point(
                    pt_array.x,
                    pt_array.y,
                    request.location.location.get("spatial_ref"),
                    esb_table)

                if results is None and service_boundary_proximity_search_policy is True:
                    # No results and Policy says we should buffer and research
                    # Create a Circle
                    # TODO remove, now in config wrapper
                    service_boundary_proximity_buffer = self._config.get('Policy',
                                                                         'service_boundary_proximity_buffer',
                                                                         as_object=False, required=False)
                    # TODO remove, now in config wrapper
                    polygon_multiple_match_policy = self._config.get('Policy', 'polygon_multiple_match_policy',
                                                                     as_object=False, required=False)
                    return_area = False
                    if polygon_multiple_match_policy == PolygonMultipleMatchPolicyEnum.ReturnAreaMajority.name:
                        return_area = True

                    return_shape = False
                    if request.serviceBoundary == 'value':
                        return_shape = True

                    results = self._db_wrapper.get_intersecting_boundaries_for_circle(
                        pt_array.x,
                        pt_array.y,
                        request.location.location.get("spatial_ref"),
                        float(service_boundary_proximity_buffer),
                        None, esb_table, return_area, return_shape)
            else:
                #Search using polygon
                results = self._db_wrapper.get_intersecting_boundaries_for_polygon(
                    request.location.location.get("vertices"),
                    request.location.location.get("spatial_ref"),
                    esb_table)

                if results is None and service_boundary_proximity_search_policy is True:
                    # No results and Policy says we should buffer and research
                    service_boundary_proximity_buffer = self._config.get('Policy',
                                                                         'service_boundary_proximity_buffer',
                                                                         as_object=False, required=False)
                    results = self._db_wrapper.get_intersecting_boundaries_for_polygon(
                        request.location.location.get("vertices"),
                        request.location.location.get("spatial_ref"),
                        esb_table, service_boundary_proximity_search_policy, service_boundary_proximity_buffer)

        return results



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

        return (results)


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




