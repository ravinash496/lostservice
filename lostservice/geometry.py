#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. currentmodule:: geometry
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

Functions for manipulating geometries.
"""

from typing import Tuple, List
import math
import numpy as np
import shapely.geometry as shp_geom
from shapely.geometry import Point
from shapely.geometry import Polygon
from shapely import affinity
from shapely.geometry.polygon import LinearRing
from shapely.wkt import loads
from geoalchemy2.shape import from_shape
from geoalchemy2.types import WKBElement
from osgeo import osr
from osgeo import ogr


def reproject_point(x: float, y: float, source_srid: int, target_srid: int) -> Tuple[float, float]:
    """
    Reproject the given point from one SR to another.

    :param x: The x coordinate of the point.
    :type x: ``float``
    :param y: The y coordinate of the point.
    :type y: ``float``
    :param source_srid:  The source spatial reference ID.
    :type source_srid: ``int``
    :param target_srid: The target spatial reference ID.
    :type target_srid: ``int``
    :return: A tuple containing the reprojected coordinates in (x,y) format.
    :rtype: :py:class`Tuple[float, float]`
    """
    # Create a geometry we can use with the transform.
    center = ogr.Geometry(ogr.wkbPoint)
    center.AddPoint(x, y)
    reproject_geom(center, source_srid, target_srid)

    return center.GetPoint()[0], center.GetPoint()[1]


def reproject_geom(geom: ogr.Geometry, source_srid: int, target_srid: int) -> ogr.Geometry:
    """
    Reproject the given geometry from one SR to another.

    :param geom: The geometry to reproject.
    :type geom: :py:class:`Geometry`
    :param source_srid: The source SRID (projection the geometry is in currently).
    :type source_srid: ``int``
    :param target_srid: the target SRID.
    :type target_srid: ``int``
    :return: The reprojected geometry.
    :rtype: :py:class:'Geometry'
    """
    # Source spatial reference in which the input geometry is projected
    source = osr.SpatialReference()
    source.ImportFromEPSG(source_srid)

    # Target spatial reference to which we want to project
    target = osr.SpatialReference()
    target.ImportFromEPSG(target_srid)

    # Set up the transform.
    transform = osr.CoordinateTransformation(source, target)

    # transform it
    geom.Transform(transform)

    return geom


def getutmsrid(longitude: float, latitude: float, incomming_srid: int = 4326) -> int:
    """
    Get the UTM SRID for the given point.

    :param latitude: latitude to find the utm srid
    :type latitude: ``float``
    :param longitude: longitude to find the utm srid
    :type longitude: ``float``
    :param incomming_srid: The input srid.
    :type incomming_srid: ``int``
    :return: UTM srid
    :rtype: ``int``
    """

    if incomming_srid != 4326:
        # Translate Coordinates from projected system into 4326 in order to calculate UTM Zone
        # Source spatial reference.
        source = osr.SpatialReference()
        source.ImportFromEPSG(incomming_srid)

        target = osr.SpatialReference()
        target.ImportFromEPSG(4326)

        # Set up the transform.
        transform = osr.CoordinateTransformation(source, target)

        # Create a geometry we can use with the transform.
        point_wkt = ogr.CreateGeometryFromWkt('POINT({0} {1})'.format(longitude, latitude))

        # Transform it and apply the buffer.
        point_wkt.Transform(transform)

        longitude = point_wkt.GetX()
        latitude = point_wkt.GetY()

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


def calculate_arc(centerx: float,
                  centery: float,
                  radius: float,
                  start_angle: float,
                  end_angle: float) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calculate lists of x and y coordinates for an arc with the given properties.

    :param centerx: X coordinate of the center of the arc.
    :type centerx: ``float``
    :param centery: Y coordinate of teh center of the arc.
    :type centery: ``float``
    :param radius: The radius of the arc.
    :type radius: ``float``
    :param start_angle: The offset angle to the start of the arc from north
    :param end_angle:
    :return: Arrays containing the x and y coordinates of the arc.
    :rtype: (np.ndarray, np.ndarray)
    """
    segments = 32

    theta = np.radians(np.linspace(start_angle, end_angle, segments))
    x = centerx + radius * np.cos(theta)
    y = centery + radius * np.sin(theta)
    return x, y


def generate_arcband(long: float,
                     lat: float,
                     spatial_ref: int,
                     band_start: float,
                     band_sweep: float,
                     inner_radius: float,
                     outer_radius: float) -> ogr.Geometry:
    """
    Generate a new arcband with the given parameters.  Assumes the center coordinates are
    in EPSG 4326, the radii are converted to UTM and the angles are in degrees.

    :param long: Longitude of the center of the arc.
    :type long: ``float``
    :param lat: Latitude of the center of the arc.
    :type lat: ``float``
    :param spatial_ref: The spatial reference for the geometry.
    :type spatial_ref: ``int``
    :param band_start: The angle of the start of the arc from north.
    :type band_start: ``float``
    :param band_sweep: The sweep angle of the arc.
    :type band_sweep: ``float``
    :param inner_radius: The distance from the center point to the inner arc.
    :type inner_radius: ``float``
    :param outer_radius: The distance from the center point to the outer radius.
    :type outer_radius: ``float``
    :return: A new arcband as an ogr Geometry object.
    :rtype: :py:class:'osgeo.ogr.Geometry`
    """
    # Pull out just the number from the SRID
    trimmed_srid = int(spatial_ref.split('::')[1])
    utmsrid = getutmsrid(long, lat, trimmed_srid)

    # project the center since the radii are in meters
    center_x, center_y = reproject_point(long, lat, trimmed_srid, utmsrid)

    # adjust for the fact that we're not doing standard geometry - back up 90 degress
    # to start from north.
    start_angle = 90 - band_start
    # find the end angle, which is the sweep relative to the start angle going clockwise so we subtract.
    end_angle = start_angle - band_sweep

    # plot a line for the outer arc.
    outer_arc_x, outer_arc_y = calculate_arc(center_x, center_y, outer_radius, start_angle, end_angle)

    # plot a line for the inner arc.
    inner_arc_x, inner_arc_y = calculate_arc(center_x, center_y, inner_radius, start_angle, end_angle)

    # reverse the inner arc to set is up to be welded to the outer arc into a polygon.
    inner_arc_x = np.flip(inner_arc_x, 0)
    inner_arc_y = np.flip(inner_arc_y, 0)

    # glue the arcs together
    band_x = np.append(outer_arc_x, inner_arc_x)
    band_y = np.append(outer_arc_y, inner_arc_y)

    # complete the ring by adding taking the first point and adding it again at the end.
    first_x = band_x[0]
    first_y = band_y[0]
    band_x = np.append(band_x, first_x)
    band_y = np.append(band_y, first_y)

    # smash the x and y arrays together to get coordinate pairs.
    ring_coordinates = np.column_stack([band_x, band_y])

    # create the polygon
    line_string = shp_geom.LinearRing(ring_coordinates)
    arc_band_polygon = shp_geom.Polygon(line_string)
    arcband = ogr.CreateGeometryFromWkb(arc_band_polygon.wkb)

    # project back to WGS84
    reproject_geom(arcband, utmsrid, 4326)

    return arcband


def get_vertices_for_geom(geom: ogr.Geometry) -> List[List[float]]:
    """
    Gets a list of the vertices for the given geometry.

    :param geom: The geomery from which points are to be extracted.
    :type geom: :py:class:`ogr.Geometry`
    :return: A list of points that compose the geometry.
    :rtype: ``[[int, int]]``
    """
    vertices = []
    geom_name = geom.GetGeometryName()
    if geom_name == 'POINT':
        vertices.append([geom.GetPoint()[0], geom.GetPoint()[1]])
    elif geom_name == 'LINEARRING':
        num_vertices = geom.GetPointCount()
        for i in range(0, geom.GetPointCount()):
            point = geom.GetPoint(i)
            vertices.append([point[0], point[1]])
    else:
        geom_count = geom.GetGeometryCount()
        for i in range(0, geom_count):
            geom_ref = geom.GetGeometryRef(i)
            verts = get_vertices_for_geom(geom_ref)
            vertices.append(verts)

    return vertices


def transform_circle(long: float, lat: float, srid: int, radius: float, uom: str) -> WKBElement:
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


def generate_circle(long: float, lat: float, srid: str, radius: float, uom: str) -> Tuple[int, WKBElement]:
    """
    Generate a circle.

    :param long: Longitude of the center of the circle.
    :type long: ``float``
    :param lat: Latitude of the center of the circle.
    :type lat: ``float``
    :param srid: The SRID of the center point.
    :type srid: ``int``
    :param radius: The radius of the circle.
    :type radius: ``float``
    :param uom: Units of measure for the radius.
    :type uom: ``str``
    :return: The projected SRID of the circle and a GeoAlchemy WKBElement representation of the circle.
    :rtype: ``(int, WKBElement)``
    """
    # Pull out just the number from the SRID
    trimmed_srid = int(srid.split('::')[1])
    long, lat = reproject_point(long, lat, trimmed_srid, 4326)

    # Get a version of the circle we can use.
    wkb_circle = transform_circle(long, lat, 4326, radius, uom)
    utmsrid = getutmsrid(long, lat)

    return utmsrid, wkb_circle


def calculate_orientation(orientation: float) -> float:
    """
    Calculates the orientation angle of an ellipse.
    :param orientation: The orientation angle of the ellipse with N as 0 going clockwise.
    :type orientation: ``float``
    :return: The new/adjusted orientation.
    :rtype: ``float``
    """
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


def transform_ellipse(long: float, lat: float, major: float, minor: float, orientation: float, srid: int) -> WKBElement:
    """
    Takes the fundamental bits of a ellipse and converts it to a descritized ellipse (polygon)
    transformed to 4326.

    :param long: Longitude of the center of the ellipse.
    :type long: ``float``
    :param lat: Latitude of the center of the ellipse.
    :type lat: ``float``
    :param major: The major axis of the ellipse.
    :type major: ``float``
    :param minor: The minor axis of the ellispe.
    :type minor: ``float``
    :param orientation: The angular orientation of the ellipse.
    :type orientation: ``float``
    :param srid: SRID of the center point.
    :type srid: ``int``
    :return: A WKB representation of the ellipse.
    :rtype: :py:class:`WKBElement`
    """

    # Source spatial reference.
    source = osr.SpatialReference()
    source.ImportFromEPSG(srid)

    # TODO - Need to handle different values for the incoming UOM
    # TODO - Must have a lookup table of some kind.
    # The target will depend on the value of uom, but we'll just assume
    # it's 9001/meters for now.
    target = osr.SpatialReference()
    # target.ImportFromEPSG(3857)
    target.ImportFromEPSG(getutmsrid(long, lat, srid))

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
    ell = affinity.scale(circle, major, minor)

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
