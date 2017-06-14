#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. currentmodule:: lostservice.db.utilities
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

General database utility functions
"""

from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.sql import select, or_
from sqlalchemy.exc import SQLAlchemyError
from lostservice.model.location import Point
from lostservice.context import PointMultipleMatchPolicyEnum
from lostservice.context import PolygonSearchModePolicyEnum
from lostservice.context import PolygonMultipleMatchPolicyEnum

class MappingDiscoveryException(Exception):
    """
    Raised when something goes wrong in the process of discovering
    the service urn to table mappings.

    :param message: The exception message
    :type message:  ``str``
    :param nested: Nested exception, if any.
    :type nested: 
    """
    def __init__(self, message, nested=None):
        super().__init__(message)
        self._nested = nested


def _get_serviceurn(tablename, engine):
    """
    Gets the service urn from a emergency services boundary table.

    :param tablename: The name of the ESB table
    :type tablename: ``str``
    :param engine: An instance of the database engine.
    :type engine:  :py:class:`sqlalchemy.engine.Engine`
    :return: ``str``
    """
    urn = None
    try:
        result = None
        tbl_metadata = MetaData(bind=engine)
        esb_table = Table(tablename, tbl_metadata, autoload=True)

        q = select([esb_table.c.serviceurn]).distinct()

        with engine.connect() as conn:
            result = conn.execute(q)
            rows = result.fetchall()
            if len(rows) > 1:
                raise MappingDiscoveryException(
                    'Table {0} contained more than one service urn: {1}'.format(tablename, rows))
            urn = rows[0]['serviceurn']

    except SQLAlchemyError as ex:
        raise MappingDiscoveryException('Failed to extract mapping for table {0}'.format(tablename), ex)
    except MappingDiscoveryException:
        raise

    return urn


def get_urn_table_mappings(engine):
    """
    Inspects the database and extracts the service urn to table mappings.

    :param engine: An instance of the database engine.
    :type engine:  :py:class:`sqlalchemy.engine.Engine`
    :return: A dictionary containing the service URNs as keys and associated table names as values
    :rtype: ``dict``
    """
    mappings = {}
    try:
        result = None
        metadata = MetaData(bind=engine, schema='information_schema')
        info_table = Table('tables', metadata, autoload=True)
        s = select([info_table.c.table_name]).where(
            or_(
                info_table.c.table_name.like('esb%'),
                info_table.c.table_name.like('aloc%')))

        with engine.connect() as conn:
            result = conn.execute(s)

            for row in result:
                tablename = row['table_name']
                urn = _get_serviceurn(tablename, engine)
                mappings[urn] = tablename

            if not mappings:
                raise MappingDiscoveryException('No service boundary tables were found in the database.')

    except SQLAlchemyError as ex:
        raise MappingDiscoveryException(
            'Encountered an error when attempting to discover the service boundary tables.', ex)
    except MappingDiscoveryException:
        raise

    return mappings


def apply_policy_settings(context, results, request):
    """
     
     :param request: 
     :return: 
     """

    if results != None:
        if len(results) == 1:
            # there is only one result return it
            return results
        else:

            polygon_search_mode_policy = context.configuration.get('Policy', 'polygon_search_mode_policy',
                                                                    as_object=False, required=False)

            # we have multiple results, then we need to apply policy to formulate the response
            if (type(request.location.location) is Point) or (polygon_search_mode_policy == PolygonSearchModePolicyEnum.SearchUsingCentroid.name):
                # This covers queries using points, or polygons centroids
                # TODO Deal with CIVIC
                point_multiple_match_policy = context.configuration.get('Policy', 'point_multiple_match_policy', as_object=False, required=False)

                if point_multiple_match_policy == PointMultipleMatchPolicyEnum.ReturnAll.name:
                    return results
                elif point_multiple_match_policy == PointMultipleMatchPolicyEnum.ReturnAllLimit5.name:
                    i = len(results)
                    del results[5:i]        # removes items starting at 5 until the end of the list
                    return results
                elif point_multiple_match_policy == PointMultipleMatchPolicyEnum.ReturnFirst.name:
                    i = len(results)
                    del results[1:i]  # removes items starting at 1 until the end of the list
                    return  results
                elif point_multiple_match_policy == PointMultipleMatchPolicyEnum.ReturnError.name:
                    raise MappingDiscoveryException('Multiple results matched request location')

            else:
                # This covers queries using polygons
                polygon_multiple_match_policy = context.configuration.get('Policy', 'polygon_multiple_match_policy',
                                                                        as_object=False, required=False)
                if polygon_multiple_match_policy == PolygonMultipleMatchPolicyEnum.ReturnAll.name:
                    return results
                elif polygon_multiple_match_policy == PolygonMultipleMatchPolicyEnum.ReturnAllLimit5.name:
                    i = len(results)
                    del results[5:i]  # removes items starting at 5 until the end of the list
                    return results
                elif polygon_multiple_match_policy == PolygonMultipleMatchPolicyEnum.ReturnFirst.name:
                    i = len(results)
                    del results[1:i]  # removes items starting at 1 until the end of the list
                    return results
                elif polygon_multiple_match_policy == PolygonMultipleMatchPolicyEnum.ReturnAreaMajority.name:
                    # Find and return Max area
                    max_area_item = max(results, key=lambda x: x['AREA_RET'])
                    lst =[max_area_item]
                    return lst
                elif polygon_multiple_match_policy == PolygonMultipleMatchPolicyEnum.ReturnError.name:
                    raise MappingDiscoveryException('Multiple results matched request location')



    return results