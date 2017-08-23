#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. currentmodule:: geometry
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

Functions for manipulating geometries.
"""

from osgeo import ogr, osr
import numpy as np
import shapely.geometry as geom
from lostservice.db.spatial import getutmsrid


def reproject_point(x, y, source_srid, target_srid):
    """
    Reproject the given point from one SR to another.

    :param x:
    :param y:
    :param source_srid:
    :param target_srid:
    :return:
    """
    # Create a geometry we can use with the transform.
    center = ogr.Geometry(ogr.wkbPoint)
    center.AddPoint(x, y)
    reproject_geom(center, source_srid, target_srid)

    return center.GetPoint()[0], center.GetPoint()[1]


def reproject_geom(geom, source_srid, target_srid):
    """
    Reproject the given geometry from one SR to another.

    :param geom:
    :param source_srid:
    :param target_srid:
    :return:
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


def calculate_arc(centerx, centery, radius, start_angle, end_angle):
    """
    Calculate lists of x and y coordinates for an arc with the given properties.

    :param centerx:
    :param centery:
    :param radius:
    :param start_angle:
    :param end_angle:
    :return:
    """
    segments = 32

    theta = np.radians(np.linspace(start_angle, end_angle, segments))
    x = centerx + radius * np.cos(theta)
    y = centery + radius * np.sin(theta)
    return x, y

    return arc


def generate_arcband(long, lat, band_start, band_sweep, inner_radius, outer_radius):
    """
    Generate a new arcband with the given parameters.  Assumes the center coordinates are
    in EPSG 4326, the radii are converted to UTM and the angles are in degrees.

    :param long:
    :param lat:
    :param band_start:
    :param band_sweep:
    :param inner_radius:
    :param outer_radius:
    :return: :py:class:'osgeo.ogr.Geometry`
    """

    utmsrid = getutmsrid(longitude=long, latitude=lat)

    # project the center since the radii are in meters
    center_x, center_y = reproject_point(long, lat, 4326, utmsrid)

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
    line_string = geom.LinearRing(ring_coordinates)
    arc_band_polygon = geom.Polygon(line_string)
    arcband = ogr.CreateGeometryFromWkb(arc_band_polygon.wkb)

    # project back to WGS84
    reproject_geom(arcband, utmsrid, 4326)

    return arcband


def get_vertices_for_geom(geom):
    """
    Gets a list of the vertices for the given geometry.

    :param geom:
    :return:
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
