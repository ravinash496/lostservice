#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: lostservice.db.gisdb
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

Database wrapper class(es)
"""

from injector import inject
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from lostservice.configuration import Configuration
import lostservice.db.spatial as spatialdb
import lostservice.db.utilities as dbutilities
from lostservice.model.geodetic import Point
from lostservice.model.geodetic import Circle
from lostservice.model.geodetic import Ellipse
from lostservice.model.geodetic import Polygon
from lostservice.model.geodetic import Arcband


class GisDbInterface(object):
    """
    Wrapper class for DB functions.
    """
    @inject
    def __init__(self, config: Configuration, engine: Engine):
        """
        Constructor.

        :param config: The configuration object.
        :type config: :py:class:`lostservice.configuration.Configuration`
        """
        self._config = config
        self._engine = engine

    def get_urn_table_mappings(self):
        """
        Inspects the database and extracts the service urn to table mappings.

        :return: A dictionary containing the service URNs as keys and associated table names as values
        :rtype: ``dict``
        """
        return dbutilities.get_urn_table_mappings(self._engine)

    def get_containing_boundary_for_point(self, location: Point, boundary_table, add_data_requested=False, buffer_distance=None):
        """
        Executes a contains query for a point.

        :param location: location object.
        :type location: :py:class:Geodetic2D
        :param boundary_table: The name of the service boundary table.
        :type boundary_table: `str`
        :return: A list of dictionaries containing the contents of returned rows.
        """
        return spatialdb.get_containing_boundary_for_point(location, boundary_table, self._engine, add_data_required=add_data_requested, buffer_distance=buffer_distance)

    def get_containing_boundary_for_circle(self, long, lat, srid, radius, uom, boundary_table):
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
        return spatialdb.get_containing_boundary_for_circle(long, lat, srid, radius, uom, boundary_table, self._engine)

    def get_intersecting_boundaries_for_circle(self, location: Circle,
                                               boundary_table: str,
                                               return_area: bool=False,
                                               return_shape: bool=False,
                                               proximity_search: bool=False,
                                               proximity_buffer = 0):
        """
        Executes an intersection query for a circle.

        :param location: location object
        :type location: :py:class:Geodetic2D
        :param boundary_table: The name of the service boundary table.
        :type boundary_table: `str`
        :param return_area: Flag which triggers an area calculation on the Intersecting polygons
        :type boundary_table: `bool`
        :return: A list of dictionaries containing the contents of returned rows.
        """
        return spatialdb.get_intersecting_boundaries_for_circle(location,
                                                                boundary_table,
                                                                self._engine,
                                                                return_area,
                                                                return_shape,
                                                                proximity_search,
                                                                proximity_buffer)

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

    def get_intersecting_boundaries_for_polygon(self, location: Polygon,
                                                boundary_table,
                                                proximity_search = False,
                                                proximity_buffer = 0 ):
        """
        Executes an intersection query for a polygon.

        :param location: location object
        :type location: :py:class:Geodetic2D
        :param boundary_table: The name of the service boundary table.
        :type boundary_table: `str`
        :return: A list of dictionaries containing the contents of returned rows.
        """
        return spatialdb.get_intersecting_boundaries_for_polygon(location,
                                                                 boundary_table,
                                                                 self._engine,
                                                                 True,
                                                                 proximity_search,
                                                                 proximity_buffer)

    def get_additionaldata_for_polygon(self, location: Polygon, boundary_table, buffer_distance ):
        """
        Executes an additional data query for a polygon.

        :param location: location object
        :type location: :py:class:Geodetic2D
        :param boundary_table: The name of the service boundary table.
        :type boundary_table: `str`
        :return: A list of dictionaries containing the contents of returned rows.
        """
        return spatialdb.get_additionaldata_for_polygon(location, boundary_table, self._engine, buffer_distance)


    def get_boundaries_for_previous_id(self, pid, boundary_table):
        """
        Executes a query to get boundaries from the previous ID.

        :param pid: `str`
        :param boundary_table: `str`
        :return: A list of dictionaries containing the contents of returned rows.
        """
        return spatialdb.get_boundaries_for_previous_id(pid, self._engine, boundary_table)

    def get_intersecting_boundary_for_ellipse(self, location: Ellipse, boundary_table):
        """
        Executes an intersection query for a ellipse.

        :param location: location object
        :type location: :py:class:Geodetic2D
        :param boundary_table: The name of the service boundary table.
        :type boundary_table: `str`
        :return: A list of dictionaries containing the contents of returned rows.
        """
        return spatialdb.get_intersecting_boundary_for_ellipse(location, boundary_table, self._engine)

    def get_additional_data_for_ellipse(self,location: Ellipse, boundary_table, buffer_distance):
        """
        Executes an intersection query for a ellipse.

        :param location: location object
        :type location: :py:class:Geodetic2D
        :param boundary_table: The name of the service boundary table.
        :type boundary_table: `str`
        :return: A list of dictionaries containing the contents of returned rows.
        """
        return spatialdb.get_additional_data_for_ellipse(location, buffer_distance, boundary_table, self._engine)

    def get_list_services_for_point(self, location: Point, boundary_table):
        """
        Executes a contains query for a point.

        :param location: location object
        :type location: :py:class:Geodetic2D
        :param boundary_table: The name of the service boundary table.
        :type boundary_table: `str`
        :return: A list of dictionaries containing the contents of returned rows.
        """
        return spatialdb.get_list_service_for_point(location, boundary_table, self._engine)

    def get_intersecting_list_service_for_circle(self, location: Circle, boundary_table, return_area=False,
                                                 return_shape=False, proximity_search=False, proximity_buffer=0):
        """
        Executes an intersection query for a circle.

        :param location: location object
        :type location: :py:class:Geodetic2D
        :param boundary_table: The name of the service boundary table.
        :type boundary_table: `str`
        :param return_area: Flag which triggers an area calculation on the Intersecting polygons
        :type return_area: `bool`
        :return: A list of dictionaries containing the contents of returned rows.
        """
        return spatialdb.get_intersecting_list_services_for_circle(location, boundary_table,
                                                                   self._engine, return_area, return_shape,
                                                                   proximity_search, proximity_buffer)

    def get_list_services_for_ellipse(self, location: Ellipse, boundary_table):
        """

        :param location: location object
        :type location: :py:class:Geodetic2D
        :param boundary_table: The name of the service boundary table.
        :type boundary_table: `str`
        :return: 
        """
        return spatialdb.get_list_services_for_ellipse(location, boundary_table,
                                                       self._engine, )

    def get_intersecting_list_service_for_polygon(self, location: Polygon,
                                                  boundary_table,
                                                  proximity_search=False,
                                                  proximity_buffer=0):
        """
        Executes an intersection query for a polygon.

        :param location: location object
        :type location: :py:class:Geodetic2D
        :param boundary_table: The name of the service boundary table.
        :type boundary_table: `str`
        :param proximity_search: Whether or not to allow the proximity buffer to be included in the search.
        :type proximity_search: `bool`
        :param proximity_buffer: A buffer around the polygon to search for extra results around the area.
        :type proximity_buffer: `float`
        :return: A list of dictionaries containing the contents of returned rows.
        """

        return spatialdb.get_intersecting_list_service_for_polygon(location, boundary_table, self._engine, False,
                                                                   proximity_search, proximity_buffer)

    def get_additional_data_for_circle(self, location: Circle, boundary_table, buffer_distance):
        """

        :param location:
        :param boundary_table: The name of the service boundary table.
        :type boundary_table: `str`
        :param buffer_distance: The distance buffered around the circle to get extra results.
        :type buffer_distance: `float`
        :return: A list of dictionaries containing the contents of returned rows.
        """
        return spatialdb.get_additional_data_for_circle(location, boundary_table, buffer_distance, self._engine)
