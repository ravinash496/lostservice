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
from sqlalchemy.sql.functions import func
from shapely.geometry import Point
from shapely import affinity
from shapely.geometry.polygon import LinearRing
from shapely.wkt import loads
from geoalchemy2.shape import from_shape
from osgeo import osr
from osgeo import ogr
import math
from lostservice.exception import InternalErrorException


class SpatialQueryException(InternalErrorException):
    """
    Raised when something goes wrong in the process of executing a spatial query.

    :param message: The exception message
    :type message:  ``str``
    :param nested: Nested exception, if any.
    :type nested:
    """
    def __init__(self, message, nested=None):
        super(SpatialQueryException, self).__init__(message, nested)


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
                # print(row)
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

        #ST_AsGML(geometry geom, integer maxdecimaldigits=15, integer options=0);
        #maxdecimaldigits = precision
        #option 16 = swap the coordinates so order is lat lon instead of database lon lat

        # Construct the "contains" query and execute it.
        s = select([the_table, func.ST_AsGML(3, the_table.c.wkb_geometry, 15, 16)],
                   the_table.c.wkb_geometry.ST_Contains(geom))


        retval = _execute_query(engine, s)

    except SQLAlchemyError as ex:
        raise SpatialQueryException(
            'Unable to construct contains query.', ex)
    except SpatialQueryException:
        raise

    return retval


def _get_nearest_point(x, y, engine, table_name, geom, buffer_distance=None):
    """
    Queries the given table for the nearest boundary

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
        utmsrid = getutmsrid(x, y)
        s = select([the_table, the_table.c.wkb_geometry.ST_AsGML(),
                    the_table.c.wkb_geometry.ST_Distance(geom).label('DISTANCE')],
                   the_table.c.wkb_geometry.ST_Intersects(
                       func.ST_Transform(
                           func.ST_Buffer(
                           func.ST_Transform(
                               func.st_centroid(geom),
                               utmsrid
                           ),buffer_distance, 32), 4326))
                   ).order_by('DISTANCE').limit(1)

        retval = _execute_query(engine, s)
    except SQLAlchemyError as ex:
        raise SpatialQueryException(
            'Unable to construct contains query.', ex)
    except SpatialQueryException:
        raise
    return retval


def _get_intersecting_boundaries_for_geom(engine, table_name, geom, return_intersection_area):
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

        # s = select([the_table, the_table.c.wkb_geometry.ST_AsGML()], the_table.c.wkb_geometry.ST_Contains(geom))

        # Construct the "intersection" query and execute
        if return_intersection_area:
            # include a calculation for the intersecting the area
            s = select(
                [the_table,
                 func.ST_AsGML(3, the_table.c.wkb_geometry, 15, 16),
                 func.ST_Area(the_table.c.wkb_geometry.ST_Intersection(func.ST_SetSRID(geom, 4326))).label('AREA_RET')
                 ],
                the_table.c.wkb_geometry.ST_Intersects(func.ST_SetSRID(geom, 4326)))
        else:

            s = select(
                [the_table,
                 func.ST_AsGML(3, the_table.c.wkb_geometry, 15, 16)],
                the_table.c.wkb_geometry.ST_Intersects(func.ST_SetSRID(geom, 4326)))

        results = _execute_query(engine, s)
    except SQLAlchemyError as ex:
        raise SpatialQueryException(
            'Unable to construct intersection query.', ex)
    except SpatialQueryException:
        raise

    return results


def _get_intersecting_boundaries_for_geom_reference(engine, table_name, geom, return_intersection_area):
    """
    Queries the given table for any boundaries that intersect the given geometry and returns the shape.

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

        # s = select([the_table, the_table.c.wkb_geometry.ST_AsGML()], the_table.c.wkb_geometry.ST_Contains(geom))

        # Construct the "intersection" query and execute
        if return_intersection_area == True:
            # include a calculation for the intersecting the area

            s = select(
                [
                    the_table,
                    func.ST_AsGML(3, the_table.c.wkb_geometry, 15, 16),
                    func.ST_Area(
                        the_table.c.wkb_geometry.ST_Intersection(func.ST_SetSRID(geom, 4326))
                    ).label('AREA_RET')
                ],
                the_table.c.wkb_geometry.ST_Intersects(func.ST_SetSRID(geom, 4326))
            )
        else:
            s = select(
                [
                    the_table,
                    func.ST_AsGML(3, the_table.c.wkb_geometry, 15, 16)
                ],
                the_table.c.wkb_geometry.ST_Intersects(func.ST_SetSRID(geom, 4326)))

        results = _execute_query(engine, s)
    except SQLAlchemyError as ex:
        raise SpatialQueryException(
            'Unable to construct intersection query.', ex)
    except SpatialQueryException:
        raise

    return results


def get_containing_boundary_for_point(x, y, srid, boundary_table, engine, add_data_required=False, buffer_distance=None):
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
    if add_data_required:
        return _get_nearest_point(x, y, engine, boundary_table, wkb_pt,buffer_distance=buffer_distance)
    return _get_containing_boundary_for_geom(engine, boundary_table, wkb_pt)


def getutmsrid(longitude, latitude):
    """

    :param latitude: latitude to find the utm srid
    :param longitude: longitude to find the utm srid
    :return: UTM srid
    """
    prefix = 0
    if latitude>0:
        '''All EPSG UTM codes in the northern hemisphere start with 326**'''
        prefix = 32600
    else:
        '''All EPSG UTM codes in the southern hemisphere start with 327**'''
        prefix = 32700

    '''UTM zones are all 6 degrees apart - 60 zones for 360 degrees
    Zone 1 starts from 180 degrees to 174 degrees west longitude
    Zone 31 starts from 0 degrees to 6 degreess east longitude

    Convert -180 to 180 degrees latitude on a 360 degree scale, 
    then divde by 6 and add 1 to get the zone number'''
    zone = int(float((longitude+180)/6))+1
    return prefix + zone


def _transform_circle(long, lat, srid, radius, uom):
    """
    Takes the fundamental bits of a circle and converts it to a descritized circle (polygon)
    transformed to 4326.

    :param long: The x coordinate of the center.
    :type long: `float`
    :param lat: The lat coordinate of the center.
    :type lat: `float`
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
    #target.ImportFromEPSG(3857)
    target.ImportFromEPSG(getutmsrid(longitude=long, latitude=lat))

    # Set up the transform.
    transform = osr.CoordinateTransformation(source, target)

    # Create a geometry we can use with the transform.
    center = ogr.CreateGeometryFromWkt('POINT({0} {1})'.format(long, lat))

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


def get_containing_boundary_for_circle(long, lat, srid, radius, uom, boundary_table, engine):
    """
    Executes a contains query for a circle.

    :param long: The x coordinate of the center.
    :type long: `float`
    :param lat: The lat coordinate of the center.
    :type lat: `float`
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
    wkb_circle = _transform_circle(long, lat, trimmed_srid, radius, uom)

    # Now execute the query.
    return _get_containing_boundary_for_geom(engine, boundary_table, wkb_circle)


def get_intersecting_boundaries_for_circle(long, lat, srid, radius, uom, boundary_table, engine, return_intersection_area=False, return_shape=False, proximity_search = False, proximity_buffer = 0):
    """    
    Executes an intersection query for a circle.

    :param long: The long coordinate of the center.
    :type long: `float`
    :param lat: The y coordinate of the center.
    :type lat: `float`
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
    :param return_intersection_area: Flag which triggers an area calculation on the Intersecting polygons
    :type return_intersection_area bool
     :param return_shape: Flag which triggers the return of the shape in GML.
    :type return_shape bool
    :return: A list of dictionaries containing the contents of returned rows.
    """

    # Pull out just the number from the SRID
    trimmed_srid = int(srid.split('::')[1])

    # Get a version of the circle we can use.
    wkb_circle = _transform_circle(long, lat, trimmed_srid, radius, uom)

    # Now execute the query.
    if return_shape == True:
        if proximity_search == True:
            return get_intersecting_boundaries_with_buffer(long, lat, engine, boundary_table, wkb_circle, proximity_buffer, return_intersection_area)
        else:
            # Call Overload to return the GML representation of the shape
            return _get_intersecting_boundaries_for_geom_reference(engine, boundary_table, wkb_circle, return_intersection_area)
    else:
        if proximity_search == True:
            return get_intersecting_boundaries_with_buffer(long, lat, engine, boundary_table, wkb_circle,
                                                           proximity_buffer, return_intersection_area)
        else:
            return _get_intersecting_boundaries_for_geom(engine, boundary_table, wkb_circle, return_intersection_area)


def get_intersecting_boundary_for_ellipse(long, lat, srid, major, minor, orientation, boundary_table, engine):
    """
    Executes a contains query for a polygon.

    :param long: longitude value .
    :type long: `float`
    :param lat: latitude value .
    :type lat: `float`
    :param srid: The spatial reference Id of the ellipse.
    :type srid: `str`
    :param major: The majorAxis value.
    :type major: `int`
    :param minor: The minorAxis value.
    :type minor: `int`
    :param orientation: The orientation of ellipse.
    :type orientation: `float`
    :param boundary_table: The name of the service boundary table.
    :type boundary_table: `str`
    :param engine: SQLAlchemy database engine.
    :type engine: :py:class:`sqlalchemy.engine.Engine`
    :return: A list of dictionaries containing the contents of returned rows.
    """


    # Pull out just the number from the SRID
    trimmed_srid = int(srid.split('::')[1])

    try:
        # Get a reference to the table we're going to look in.
        tbl_metadata = MetaData(bind=engine)
        the_table = Table(boundary_table, tbl_metadata, autoload=True)

        utmsrid = getutmsrid(longitude=long, latitude=lat)

        wkb_ellipse = _transform_ellipse(long ,lat , major, minor, orientation, trimmed_srid)

        s = select(
            [
                the_table,
                func.ST_AsGML(3, the_table.c.wkb_geometry.ST_Dump().geom, 15, 16),
                the_table.c.wkb_geometry.ST_Area(
                    the_table.c.wkb_geometry.ST_Intersects(wkb_ellipse)
                ).label('AREA_RET')
            ],
            the_table.c.wkb_geometry.ST_Intersects(wkb_ellipse)
        )

        results = _execute_query(engine, s)
    except SQLAlchemyError as ex:
        raise SpatialQueryException(
            'Unable to construct ellipse intersection query.', ex)
    except SpatialQueryException:
        raise
    return results

def _transform_ellipse(long ,lat , major, minor, orientation, srid):
    """
    Takes the fundamental bits of a ellipse and converts it to a descritized ellipse (polygon)
    transformed to 4326.
    :param long: 
    :param lat: 
    :param major: 
    :param minor: 
    :param orientation: 
    :param srid: 
    :return: 
    """

    # Source spatial reference.
    source = osr.SpatialReference()
    source.ImportFromEPSG(srid)

    # TODO - Need to handle different values for the incoming UOM
    # TODO - Must have a lookup table of some kind.
    # The target will depend on the value of uom, but we'll just assume
    # it's 9001/meters for now and project to 3857.
    target = osr.SpatialReference()
    # target.ImportFromEPSG(3857)
    target.ImportFromEPSG(getutmsrid(longitude=long, latitude=lat))

    # Set up the transform.
    transform = osr.CoordinateTransformation(source, target)

    # Create a geometry we can use with the transform.
    center = ogr.CreateGeometryFromWkt('POINT({0} {1})'.format(long, lat))

    # Transform it and apply the buffer.
    center.Transform(transform)
    cir = center.Buffer(1)

    wkt_cir = cir.ExportToWkt()

    # load up a new Shapely Polygon from the WKT and convert it to a GeoAlchemy2 WKBElement
    # that we can use to query.
    circle = loads(wkt_cir)

    # Let create the ellipse along x and y:
    ell = affinity.scale(circle,
                            major,
                            minor)

    # xml.py parse method has already converted GML degree's to radians
    rotate_angle = calculate_orientation(orientation)


    if rotate_angle >= 0:
        # Let rotate the ellipse (clockwise, x axis pointing right):
        ellr = affinity.rotate(ell, rotate_angle, use_radians=True)
    else:
        # If one need to rotate it clockwise along an upward pointing x axis:
        ellr = affinity.rotate(ell, 90 - rotate_angle, use_radians=True)
        # According to the man, a positive value means a anti-clockwise angle,
        # and a negative one a clockwise angle.

    # Convert from shapely to org
    org_ellipse = ogr.CreateGeometryFromWkt(ellr.wkt)

    # Now transform it back to 4326 and extract the wkt
    reverse_transform = osr.CoordinateTransformation(target, source)
    org_ellipse.Transform(reverse_transform)
    wkt_ellipse = org_ellipse.ExportToWkt()

    # load up a new Shapely Polygon from the WKT and convert it to a GeoAlchemy2 WKBElement
    # that we can use to query.
    poly = loads(wkt_ellipse)
    wkb_ellipse = from_shape(poly, srid)

    return wkb_ellipse


def calculate_orientation(orientation):
    # The angle input is assumed to be from North going clockwise in GML, but postgis will start at the x-axis going
    # couterclockwise, so we need to adjust the angle of the original GML value to match postgis

    # Mod the angle by 2pi to make sure it is within one revolution
    rotate_angle = orientation % (2 * math.pi)
    # Subtract angle from 2pi to get reverse angle, or if it is negative just negate it (to make it positive)
    if rotate_angle < 0:
        rotate_angle = -1 * rotate_angle
    else:
        rotate_angle = (2 * math.pi) - rotate_angle

    # Offset by pi/2 to get angle from horizontal x-axis instead of y-axis(North)
    rotate_angle = rotate_angle + (math.pi / 2)

    # Re-mod the angle by 2pi as we could have gone beyond 2pi when we adjusted from y-axis to x-axis based angle
    rotate_angle = rotate_angle % (2 * math.pi)

    # Fix floating point errors
    if rotate_angle - math.floor(rotate_angle) < 0.00000001:
        rotate_angle = math.floor(rotate_angle)

    return rotate_angle

def get_containing_boundary_for_polygon(points, srid, boundary_table, engine, proximity_search = False, proximity_buffer = 0 ):
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

    if proximity_search == True:
        get_intersecting_boundaries_with_buffer(points[0][0], points[0][1], engine, boundary_table, wkb_ring, proximity_buffer)
    else:
        return _get_containing_boundary_for_geom(engine, boundary_table, wkb_ring)


def get_intersecting_boundaries_for_polygon(points, srid, boundary_table, engine, return_intersection_area=False, proximity_search = False, proximity_buffer = 0 ):
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
    :param return_intersection_area: Flag which triggers an area calculation on the Intersecting polygons
    :type return_intersection_area bool
    :return: A list of dictionaries containing the contents of returned rows.
    """
    # Pull out just the number from the SRID
    trimmed_srid = srid.split('::')[1]

    ring = LinearRing(points)
    wkb_ring = from_shape(ring, trimmed_srid)

    if proximity_search == True:
        return get_intersecting_boundaries_with_buffer(points[0][0], points[0][1], engine, boundary_table, wkb_ring,
                                                proximity_buffer, return_intersection_area)
    else:
        return _get_intersecting_boundaries_for_geom(engine, boundary_table, wkb_ring, return_intersection_area)


def get_boundaries_for_previous_id(pid, engine, boundary_table):
    """
    Executes an query to get the boundary.

    :param pid: previously returned id.
    :type pid: `text`
    :param boundary_table: The name of the service boundary table.
    :type boundary_table: `str`
    :param engine: SQLAlchemy database engine.
    :type engine: :py:class:`sqlalchemy.engine.Engine`
    :return: A list of dictionaries containing the contents of returned rows.
    """
    try:
        # Get a reference to the table we're going to look in.
        tbl_metadata = MetaData(bind=engine)
        the_table = Table(boundary_table, tbl_metadata, autoload=True)

        s = select([the_table, the_table.c.wkb_geometry.ST_AsGML()],
                   the_table.c.gcunqid.like(pid))

        results = _execute_query(engine, s)
    except SQLAlchemyError as ex:
        raise SpatialQueryException(
            'Unable to construct boundaries query.', ex)
    except SpatialQueryException:
        raise

    return results


def get_intersecting_boundaries_with_buffer(long, lat, engine, table_name, geom, buffer_distance, return_intersection_area = False):
    retval = None
    try:
        # Get a reference to the table we're going to look in.
        tbl_metadata = MetaData(bind=engine)
        the_table = Table(table_name, tbl_metadata, autoload=True)

        # Construct the "contains" query and execute it.
        utmsrid = getutmsrid(longitude=long, latitude=lat)

        if return_intersection_area:
        # include a calculation for the intersecting the area

            s = select([the_table, the_table.c.wkb_geometry.ST_AsGML(), func.ST_Area(
            func.ST_Intersection(
                func.ST_Buffer(func.ST_Transform(func.ST_SetSRID(geom, 4326), utmsrid), buffer_distance), the_table.c.wkb_geometry.ST_Transform(utmsrid))).label(
            'AREA_RET')],
                   func.ST_Intersects(
                       func.ST_Buffer(func.ST_Transform(func.ST_SetSRID(geom, 4326), utmsrid), buffer_distance),
                       the_table.c.wkb_geometry.ST_Transform(utmsrid)))


        else:

            s = select([the_table, the_table.c.wkb_geometry.ST_AsGML()],
                   func.ST_Intersects(func.ST_Buffer(func.ST_Transform(func.ST_SetSRID(geom,4326), utmsrid), buffer_distance),
                                      the_table.c.wkb_geometry.ST_Transform(utmsrid)))



        retval = _execute_query(engine, s)

    except SQLAlchemyError as ex:
        raise SpatialQueryException(
            'Unable to construct contains query.', ex)
    except SpatialQueryException:
        raise

    return retval


def get_list_service_for_point(x, y, srid, boundary_table, engine):
    """

    :param x: 
    :param y: 
    :param srid: 
    :param boundary_table: 
    :param engine: 
    :return: 
    """
    # Create a Shapely Point
    pt = Point(x, y)

    # Pull out just the number from the SRID
    trimmed_srid = srid.split('::')[1]

    # Get a GeoAlchemy WKBElement from the point.
    wkb_pt = from_shape(pt, trimmed_srid)
    # Run the query.
    return (_get_list_service_for_geom(engine, i, wkb_pt) for i in boundary_table)


def get_intersecting_list_services_for_circle(long, lat, srid, radius, uom, boundary_table, engine, return_intersection_area=False, return_shape=False, proximity_search = False, proximity_buffer = 0):
    """    
    Executes an intersection query for a circle.

    :param long: The long coordinate of the center.
    :type long: `float`
    :param lat: The y coordinate of the center.
    :type lat: `float`
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
    :param return_intersection_area: Flag which triggers an area calculation on the Intersecting polygons
    :type return_intersection_area bool
     :param return_shape: Flag which triggers the return of the shape in GML.
    :type return_shape bool
    :return: A list of dictionaries containing the contents of returned rows.
    """

    # Pull out just the number from the SRID
    trimmed_srid = int(srid.split('::')[1])

    # Get a version of the circle we can use.
    wkb_circle = _transform_circle(long, lat, trimmed_srid, radius, uom)

    # Now execute the query.

    return (_get_intersecting_list_service_for_geom(engine, i, wkb_circle, return_intersection_area) for i in boundary_table)


def get_intersecting_list_service_for_polygon(points, srid, boundary_table, engine, return_intersection_area=False, proximity_search = False, proximity_buffer = 0 ):
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
    :param return_intersection_area: Flag which triggers an area calculation on the Intersecting polygons
    :type return_intersection_area bool
    :return: A list of dictionaries containing the contents of returned rows.
    """
    # Pull out just the number from the SRID
    trimmed_srid = srid.split('::')[1]

    ring = LinearRing(points)
    wkb_ring = from_shape(ring, trimmed_srid)

    return (_get_intersecting_list_service_for_geom(engine, i, wkb_ring, return_intersection_area) for i in
            boundary_table)


def get_list_services_for_ellipse(lat, long, srid, major, minor, orientation, boundary_table, engine):

    return (_get_list_services_for_ellipse(lat, long, srid, major, minor, orientation, i, engine) for i in boundary_table)


def _get_list_services_for_ellipse(lat, long, srid, major, minor, orientation, boundary_table, engine):
    """
    Executes a contains query for a polygon.

    :param lat: latitude value .
    :type lat: `float`
    :param long: longitude value .
    :type long: `float`
    :param srid: The spatial reference Id of the ellipse.
    :type srid: `str`
    :param major: The majorAxis value.
    :type major: `int`
    :param minor: The minorAxis value.
    :type minor: `int`
    :param orientation: The orientation of ellipse.
    :type orientation: `float`
    :param boundary_table: The name of the service boundary table.
    :type boundary_table: `str`
    :param engine: SQLAlchemy database engine.
    :type engine: :py:class:`sqlalchemy.engine.Engine`
    :return: A list of dictionaries containing the contents of returned rows.
    """
    # Pull out just the number from the SRID

    trimmed_srid = int(srid.split('::')[1])

    try:
        # Get a reference to the table we're going to look in.
        tbl_metadata = MetaData(bind=engine)
        the_table = Table(boundary_table, tbl_metadata, autoload=True)

        utmsrid = getutmsrid(longitude=long, latitude=lat)

        wkb_ellipse = _transform_ellipse(long, lat, major, minor, orientation, trimmed_srid)

        s = select(
            [
                the_table.c.serviceurn,
                func.ST_AsGML(3, the_table.c.wkb_geometry.ST_Dump().geom, 15, 16),
                the_table.c.wkb_geometry.ST_Area(
                    the_table.c.wkb_geometry.ST_Intersects(wkb_ellipse)
                ).label('AREA_RET')
            ],
            the_table.c.wkb_geometry.ST_Intersects(wkb_ellipse)
        )

        results = _execute_query(engine, s)
    except SQLAlchemyError as ex:
        raise SpatialQueryException(
            'Unable to construct ellipse intersection query.', ex)
    except SpatialQueryException:
        raise
    return results


def get_intersecting_list_service_with_buffer(long, lat, engine, table_name, geom, buffer_distance, return_intersection_area = False):
    retval = None
    try:
        # Get a reference to the table we're going to look in.
        tbl_metadata = MetaData(bind=engine)
        the_table = Table(table_name, tbl_metadata, autoload=True)

        # Construct the "contains" query and execute it.
        utmsrid = getutmsrid(longitude=long, latitude=lat)

        if return_intersection_area:
        # include a calculation for the intersecting the area

            s = select([the_table.c.serviceurn, the_table.c.wkb_geometry.ST_AsGML(), func.ST_Area(
            func.ST_Intersection(
                func.ST_Buffer(func.ST_Transform(func.ST_SetSRID(geom, 4326), utmsrid), buffer_distance), the_table.c.wkb_geometry.ST_Transform(utmsrid))).label(
            'AREA_RET')],
                   func.ST_Intersects(
                       func.ST_Buffer(func.ST_Transform(func.ST_SetSRID(geom, 4326), utmsrid), buffer_distance),
                       the_table.c.wkb_geometry.ST_Transform(utmsrid)))


        else:

            s = select([the_table.c.serviceurn, the_table.c.wkb_geometry.ST_AsGML()],
                   func.ST_Intersects(func.ST_Buffer(func.ST_Transform(func.ST_SetSRID(geom,4326), utmsrid), buffer_distance),
                                      the_table.c.wkb_geometry.ST_Transform(utmsrid)))



        retval = _execute_query(engine, s)

    except SQLAlchemyError as ex:
        raise SpatialQueryException(
            'Unable to construct contains query.', ex)
    except SpatialQueryException:
        raise

    return retval


def _get_intersecting_list_service_for_geom(engine, table_name, geom, return_intersection_area):
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

        # s = select([the_table, the_table.c.wkb_geometry.ST_AsGML()], the_table.c.wkb_geometry.ST_Contains(geom))

        # Construct the "intersection" query and execute
        if return_intersection_area:
            # include a calculation for the intersecting the area
            s = select(
                [the_table.c.serviceurn, func.ST_Area(
                    the_table.c.wkb_geometry.ST_Intersection(func.ST_SetSRID(geom, 4326))).label('AREA_RET')],
                the_table.c.wkb_geometry.ST_Intersects(func.ST_SetSRID(geom, 4326)))
        else:

            s = select(
                [the_table.c.serviceurn, func.ST_AsGML(3, the_table.c.wkb_geometry, 15, 16)],
                the_table.c.wkb_geometry.ST_Intersects(func.ST_SetSRID(geom, 4326)))

        results = _execute_query(engine, s)
    except SQLAlchemyError as ex:
        raise SpatialQueryException(
            'Unable to construct intersection query.', ex)
    except SpatialQueryException:
        raise

    return results


def _get_list_service_for_geom(engine, table_name, geom):
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
        s = select([the_table.c.serviceurn], the_table.c.wkb_geometry.ST_Contains(geom))
        retval = _execute_query(engine, s)
    except SQLAlchemyError as ex:
        raise SpatialQueryException(
            'Unable to construct contains query.', ex)
    except SpatialQueryException:
        raise
    return retval