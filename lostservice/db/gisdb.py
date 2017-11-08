#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: lostservice.db.gisdb
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

Database wrapper class(es)
"""

from injector import inject
from sqlalchemy import create_engine
from lostservice.configuration import Configuration
import lostservice.db.spatial as spatialdb
import lostservice.db.utilities as dbutilities


class GisDbInterface(object):
    """
    Wrapper class for DB functions.
    """
    @inject
    def __init__(self, config: Configuration):
        """
        Constructor.

        :param config: The configuration object.
        :type config: :py:class:`lostservice.configuration.Configuration`
        """
        self._config = config
        self._engine = self._create_engine_internal()

    def _create_engine_internal(self):
        """
        Internal method to create the SQLAlchemy engine which can be mocked for testing.

        :return: SQLAlchemy database engine.
        :rtype: :py:class:`sqlalchemy.engine.Engine`
        """
        return create_engine(self._config.get_gis_db_connection_string())

    def get_urn_table_mappings(self):
        """
        Inspects the database and extracts the service urn to table mappings.

        :return: A dictionary containing the service URNs as keys and associated table names as values
        :rtype: ``dict``
        """
        return dbutilities.get_urn_table_mappings(self._engine)

    def get_containing_boundary_for_point(self, location, boundary_table, add_data_requested=False, buffer_distance=None):
        """
        Executes a contains query for a point.

        :param location: location object.
        :type location: `location object`
        :param boundary_table: The name of the service boundary table.
        :type boundary_table: `str`
        :return: A list of dictionaries containing the contents of returned rows.
        """
        return spatialdb.get_containing_boundary_for_point(location, boundary_table, self._engine, add_data_required=add_data_requested, buffer_distance=buffer_distance)

    def get_containing_boundary_for_circle(self, location, radius, uom, boundary_table):
        """
        Executes a contains query for a circle.

        :param location: location object.
        :type location: `location object`
        :param radius: The radius of the circle.
        :type radius: `float`
        :param uom: The unit of measure of the radius.
        :type uom: `str`
        :param boundary_table: The name of the service boundary table.
        :type boundary_table: `str`
        :return: A list of dictionaries containing the contents of returned rows.
        """
        return spatialdb.get_containing_boundary_for_circle(location, radius, uom, boundary_table, self._engine)

    def get_intersecting_boundaries_for_circle(self, location, radius, uom, boundary_table, return_area = False, return_shape = False, proximity_search = False, proximity_buffer = 0):
        """
        Executes an intersection query for a circle.

        :param long: The long coordinate of the center.
        :type long: `float`
        :param lat: The y coordinate of the center.
        :type y: `float`
        :param srid: The spatial reference id of the center point.
        :type srid: `str`
        :param radius: The radius of the circle.
        :type radius: `float`
        :param uom: The unit of measure of the radius.
        :type uom: `str`
        :param boundary_table: The name of the service boundary table.
        :type boundary_table: `str`
        :param return_area: Flag which triggers an area calculation on the Intersecting polygons
        :type boundary_table: `bool`
        :return: A list of dictionaries containing the contents of returned rows.
        """
        return spatialdb.get_intersecting_boundaries_for_circle(location, radius, uom, boundary_table, self._engine, return_area, return_shape, proximity_search, proximity_buffer)

    def get_containing_boundary_for_polygon(self, points, srid, boundary_table):
        """
        Executes a contains query for a polygon.

        :param points: A list of vertices in (x,y) format.
        :type points: `list`
        :param srid: The spatial reference Id of the vertices.
        :type srid: `str`
        :param boundary_table: The name of the service boundary table.
        :type boundary_table: `str`
        :return: A list of dictionaries containing the contents of returned rows.
        """
        return spatialdb.get_containing_boundary_for_polygon(points, srid, boundary_table, self._engine)

    def get_intersecting_boundaries_for_polygon(self, points, srid, boundary_table, proximity_search = False, proximity_buffer = 0 ):
        """
        Executes an intersection query for a polygon.

        :param points: A list of vertices in (x,y) format.
        :type points: `list`
        :param srid: The spatial reference Id of the vertices.
        :type srid: `str`
        :param boundary_table: The name of the service boundary table.
        :type boundary_table: `str`
        :return: A list of dictionaries containing the contents of returned rows.
        """
        return spatialdb.get_intersecting_boundaries_for_polygon(points, srid, boundary_table, self._engine, True, proximity_search, proximity_buffer)

    def get_additionaldata_for_polygon(self, points, srid, boundary_table, buffer_distance ):
        """
        Executes an additonal data query for a polygon.

        :param points: A list of vertices in (x,y) format.
        :type points: `list`
        :param srid: The spatial reference Id of the vertices.
        :type srid: `str`
        :param boundary_table: The name of the service boundary table.
        :type boundary_table: `str`
        :return: A list of dictionaries containing the contents of returned rows.
        """
        return spatialdb.get_additionaldata_for_polygon(points, srid, boundary_table, self._engine, buffer_distance)


    def get_boundaries_for_previous_id(self, pid, boundary_table):
        return spatialdb.get_boundaries_for_previous_id(pid, self._engine, boundary_table)

    def get_intersecting_boundary_for_ellipse(self, long, lat, srid, major, minor, orientation, boundary_table):
        return spatialdb.get_intersecting_boundary_for_ellipse(long, lat, srid, major, minor, orientation, boundary_table, self._engine)

    def get_additional_data_for_ellipse(self, long, lat, srid, major, minor, orientation, boundary_table, buffer_distance):
        return spatialdb.get_additional_data_for_ellipse(long, lat, srid, major, minor, orientation,buffer_distance, boundary_table, self._engine)

    def get_list_services_for_point(self, long, lat, srid, boundary_table):
        """
        Executes a contains query for a point.

        :param long: The x coordinate of the point.
        :type long: `float`
        :param lat: The y coordinate of the point.
        :type lat: `float`
        :param srid: The spatial reference Id of the point.
        :type srid: `str`
        :param boundary_table: The name of the service boundary table.
        :type boundary_table: `str`
        :return: A list of dictionaries containing the contents of returned rows.
        """
        return spatialdb.get_list_service_for_point(long, lat, srid, boundary_table, self._engine)

    def get_intersecting_list_service_for_circle(self, long, lat, srid, radius, uom, boundary_table, return_area=False,
                                                 return_shape=False, proximity_search=False, proximity_buffer=0):
        """
        Executes an intersection query for a circle.

        :param long: The long coordinate of the center.
        :type long: `float`
        :param lat: The y coordinate of the center.
        :type y: `float`
        :param srid: The spatial reference id of the center point.
        :type srid: `str`
        :param radius: The radius of the circle.
        :type radius: `float`
        :param uom: The unit of measure of the radius.
        :type uom: `str`
        :param boundary_table: The name of the service boundary table.
        :type boundary_table: `str`
        :param return_area: Flag which triggers an area calculation on the Intersecting polygons
        :type boundary_table: `bool`
        :return: A list of dictionaries containing the contents of returned rows.
        """
        return spatialdb.get_intersecting_list_services_for_circle(long, lat, srid, radius, uom, boundary_table,
                                                                   self._engine, return_area, return_shape,
                                                                   proximity_search, proximity_buffer)

    def get_list_services_for_ellipse(self, long, lat, srid, major, minor, orientation, boundary_table):
        """

        :param lat: 
        :param long: 
        :param srid: 
        :param major: 
        :param minor: 
        :param orientation: 
        :param boundary_table: 
        :return: 
        """
        return spatialdb.get_list_services_for_ellipse(long, lat, srid, major, minor, orientation, boundary_table,
                                                       self._engine, )

    def get_intersecting_list_service_for_polygon(self, points, srid, boundary_table, proximity_search=False,
                                                  proximity_buffer=0):
        """
        Executes an intersection query for a polygon.

        :param points: A list of vertices in (x,y) format.
        :type points: `list`
        :param srid: The spatial reference Id of the vertices.
        :type srid: `str`
        :param boundary_table: The name of the service boundary table.
        :type boundary_table: `str`
        :return: A list of dictionaries containing the contents of returned rows.
        """

        return spatialdb.get_intersecting_list_service_for_polygon(points, srid, boundary_table, self._engine, False,
                                                                   proximity_search, proximity_buffer)

    def get_additional_data_for_circle(self, long, lat, srid, radius, uom, boundary_table, buffer_distance):
        return spatialdb.get_additional_data_for_circle(long, lat, srid, radius, uom, boundary_table, buffer_distance, self._engine)

