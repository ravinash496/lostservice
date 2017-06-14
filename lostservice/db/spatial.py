#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. currentmodule:: lostservice.db.spatial
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

Spatial DB functions.
TODO: This code currently does not deal with any projections that will be required
to transform incoming coordinates to 4326 which is our standard.
"""

from sqlalchemy import MetaData, Table
from sqlalchemy.sql import select
from sqlalchemy.exc import SQLAlchemyError
from shapely.geometry import Point
from shapely.geometry.polygon import LinearRing
from shapely.wkt import loads
from geoalchemy2.shape import from_shape
from osgeo import osr
from osgeo import ogr


class SpatialQueryException(Exception):
    """
    Raised when something goes wrong in the process of executing a spatial query.

    :param message: The exception message
    :type message:  ``str``
    :param nested: Nested exception, if any.
    :type nested:
    """
    def __init__(self, message, nested=None):
        super().__init__(message)
        self._nested = nested


def _execute_query(engine, query):
    """
    Execute the given query.  Handles connecting and cleanup.

    :param engine: SQLAlchemy database engine.
    :type engine: :py:class:`sqlalchemy.engine.Engine`
    :param query: The query to execute (created by calling SQLAlchemy select() function).
    :type query: :py:class:`sqlalchemy.sql.expression.Select
    :return: A list of dictionaries containing returned rows and their contents.
    """
    retval = []
    try:
        with engine.connect() as conn:
            result = conn.execute(query)
            for row in result:
                row_copy = dict(zip(row.keys(), row))
                retval.append(row_copy)
            result.close()

    except SQLAlchemyError as ex:
        raise SpatialQueryException(
            'Spatial query failed with an error.', ex)

    return retval if retval else None


# TODO - We could probably use a decorator to handle the repeated work
# TODO - of setting up the table reference and exception handling
# TODO - in the two functions below.


def _get_containing_boundary_for_geom(engine, table_name, geom):
    """
    Queries the given table for the boundary in which the given
    geometry falls.

    :param engine: SQLAlchemy database engine
    :type engine: :py:class:`sqlalchemy.engine.Engine`
    :param table_name: The name of the service boundary table.
    :type table_name: `str`
    :param geom: The geometry to use in the search as a GeoAlchemy WKBElement.
    :type geom: :py:class:geoalchemy2.types.WKBElement
    :return: A list of dictionaries containing the contents of returned rows.
    """
    retval = None
    try:
        # Get a reference to the table we're going to look in.
        tbl_metadata = MetaData(bind=engine)
        the_table = Table(table_name, tbl_metadata, autoload=True)

        # Construct the "contains" query and execute it.
        s = select([the_table], the_table.c.wkb_geometry.ST_Contains(geom))
        retval = _execute_query(engine, s)
    except SQLAlchemyError as ex:
        raise SpatialQueryException(
            'Unable to construct contains query.', ex)
    except SpatialQueryException:
        raise

    return retval


def _get_intersecting_boundaries_for_geom(engine, table_name, geom):
    """
    Queries the given table for any boundaries that intersect the given geometry.

    :param engine: SQLAlchemy database engine
    :type engine: :py:class:`sqlalchemy.engine.Engine`
    :param table_name: The name of the service boundary table.
    :type table_name: `str`
    :param geom: The geometry to use in the search as a GeoAlchemy WKBElement.
    :type geom: :py:class:geoalchemy2.types.WKBElement
    :return: A list of dictionaries containing the contents of returned rows.
    """
    retval = None
    try:
        # Get a reference to the table we're going to look in.
        tbl_metadata = MetaData(bind=engine)
        the_table = Table(table_name, tbl_metadata, autoload=True)

        # Construct the "intersection" query and execute
        s = select([the_table], the_table.c.wkb_geometry.ST_Intersects(geom))
        results = _execute_query(engine, s)
    except SQLAlchemyError as ex:
        raise SpatialQueryException(
            'Unable to construct intersection query.', ex)
    except SpatialQueryException:
        raise

    return results


def get_containing_boundary_for_point(x, y, srid, boundary_table, engine):
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
    :param engine: SQLAlchemy database engine.
    :type engine: :py:class:`sqlalchemy.engine.Engine`
    :return: A list of dictionaries containing the contents of returned rows.
    """
    # Create a Shapely Point
    pt = Point(x, y)

    # Pull out just the number from the SRID
    trimmed_srid = srid.split('::')[1]

    # Get a GeoAlchemy WKBElement from the point.
    wkb_pt = from_shape(pt, trimmed_srid)
    # Run the query.
    return _get_containing_boundary_for_geom(engine, boundary_table, wkb_pt)


def _transform_circle(x, y, srid, radius, uom):
    """
    Takes the fundamental bits of a circle and converts it to a descritized circle (polygon)
    transformed to 4326.

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
    :return: A WKBElement representation of the circle.
    :rtype: :py:class:geoalchemy2.types.WKBElement
    """

    # Source spatial reference.
    source = osr.SpatialReference()
    source.ImportFromEPSG(srid)

    # TODO - Need to handle different values for the incoming UOM
    # TODO - Must have a lookup table of some kind.
    # The target will depend on the value of uom, but we'll just assume
    # it's 9001/meters for now and project to 3857.
    target = osr.SpatialReference()
    target.ImportFromEPSG(3857)

    # Set up the transform.
    transform = osr.CoordinateTransformation(source, target)

    # Create a geometry we can use with the transform.
    center = ogr.CreateGeometryFromWkt('POINT({0} {1})'.format(x, y))

    # Transform it and apply the buffer.
    center.Transform(transform)
    circle = center.Buffer(radius)

    # Now transform it back and extract the wkt
    reverse_transform = osr.CoordinateTransformation(target, source)
    circle.Transform(reverse_transform)
    wkt_circle = circle.ExportToWkt()

    # load up a new Shapely Polygon from the WKT and convert it to a GeoAlchemy2 WKBElement
    # that we can use to query.
    poly = loads(wkt_circle)
    wkb_circle = from_shape(poly, srid)

    return wkb_circle


def get_containing_boundary_for_circle(x, y, srid, radius, uom, boundary_table, engine):
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
    :param engine: SQLAlchemy database engine.
    :type engine: :py:class:`sqlalchemy.engine.Engine`
    :return: A list of dictionaries containing the contents of returned rows.
    """

    # Pull out just the number from the SRID
    trimmed_srid = srid.split('::')[1]

    # Get a version of the circle we can use.
    wkb_circle = _transform_circle(x, y, trimmed_srid, radius, uom)

    # Now execute the query.
    return _get_containing_boundary_for_geom(engine, boundary_table, wkb_circle)


def get_intersecting_boundaries_for_circle(x, y, srid, radius, uom, boundary_table, engine):
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
    :param engine: SQLAlchemy database engine.
    :type engine: :py:class:`sqlalchemy.engine.Engine`
    :return: A list of dictionaries containing the contents of returned rows.
    """

    # Pull out just the number from the SRID
    trimmed_srid = int(srid.split('::')[1])

    # Get a version of the circle we can use.
    wkb_circle = _transform_circle(x, y, trimmed_srid, radius, uom)

    # Now execute the query.
    return _get_intersecting_boundaries_for_geom(engine, boundary_table, wkb_circle)


def get_containing_boundary_for_polygon(points, srid, boundary_table, engine):
    """
    Executes a contains query for a polygon.

    :param points: A list of vertices in (x,y) format.
    :type points: `list`
    :param srid: The spatial reference Id of the vertices.
    :type srid: `str`
    :param boundary_table: The name of the service boundary table.
    :type boundary_table: `str`
    :param engine: SQLAlchemy database engine.
    :type engine: :py:class:`sqlalchemy.engine.Engine`
    :return: A list of dictionaries containing the contents of returned rows.
    """
    # Pull out just the number from the SRID
    trimmed_srid = srid.split('::')[1]

    ring = LinearRing(points)
    wkb_ring = from_shape(ring, trimmed_srid)
    return _get_containing_boundary_for_geom(engine, boundary_table, wkb_ring)


def get_intersecting_boundaries_for_polygon(points, srid, boundary_table, engine):
    """
    Executes an intersection query for a polygon.

    :param points: A list of vertices in (x,y) format.
    :type points: `list`
    :param srid: The spatial reference Id of the vertices.
    :type srid: `str`
    :param boundary_table: The name of the service boundary table.
    :type boundary_table: `str`
    :param engine: SQLAlchemy database engine.
    :type engine: :py:class:`sqlalchemy.engine.Engine`
    :return: A list of dictionaries containing the contents of returned rows.
    """
    # Pull out just the number from the SRID
    trimmed_srid = srid.split('::')[1]

    ring = LinearRing(points)
    wkb_ring = from_shape(ring, trimmed_srid)
    return _get_intersecting_boundaries_for_geom(engine, boundary_table, wkb_ring)

