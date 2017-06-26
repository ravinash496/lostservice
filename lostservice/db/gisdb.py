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
        return create_engine(self._config.get_db_connection_string())

    def get_urn_table_mappings(self):
        """
        Inspects the database and extracts the service urn to table mappings.

        :return: A dictionary containing the service URNs as keys and associated table names as values
        :rtype: ``dict``
        """
        return dbutilities.get_urn_table_mappings(self._engine)

    def get_containing_boundary_for_point(self, x, y, srid, boundary_table):
        """
        Executes a contains query for a point.

        :param x: The x coordinate of the point.
        :type x: `float`
        :param y: The y coordinate of the point.
        :type y: `float`
        :param srid: The spatial reference Id of the point.
        :type srid: `str`
        :param boundary_table: The name of the service boundary table.
        :type boundary_table: `str`
        :return: A list of dictionaries containing the contents of returned rows.
        """
        return spatialdb.get_containing_boundary_for_point(x, y, srid, boundary_table, self._engine)

    def get_containing_boundary_for_circle(self, x, y, srid, radius, uom, boundary_table):
        """
        Executes a contains query for a circle.

        :param x: The x coordinate of the center.
        :type x: `float`
        :param y: The y coordinate of the center.
        :type y: `float`
        :param srid: The spatial reference id of the center point.
        :type srid: `str`
        :param radius: The radius of the circle.
        :type radius: `float`
        :param uom: The unit of measure of the radius.
        :type uom: `str`
        :param boundary_table: The name of the service boundary table.
        :type boundary_table: `str`
        :return: A list of dictionaries containing the contents of returned rows.
        """
        return spatialdb.get_containing_boundary_for_circle(x,y, srid, radius, uom, boundary_table, self._engine)

    def get_intersecting_boundaries_for_circle(self, x, y, srid, radius, uom, boundary_table, return_area = False, return_shape = False):
        """
        Executes an intersection query for a circle.

        :param x: The x coordinate of the center.
        :type x: `float`
        :param y: The y coordinate of the center.
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
        return spatialdb.get_intersecting_boundaries_for_circle(x, y, srid, radius, uom, boundary_table, self._engine, return_area, return_shape)

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

    def get_intersecting_boundaries_for_polygon(self, points, srid, boundary_table):
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
        return spatialdb.get_containing_boundary_for_polygon(points, srid, boundary_table, self._engine)


    def get_boundaries_for_previous_id(self, pid, boundary_table):
        return spatialdb.get_boundaries_for_previous_id(pid, self._engine, boundary_table)