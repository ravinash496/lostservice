#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: lostservice.model.geodetic
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

Models for different types of geodetic locations.
"""

from abc import ABCMeta, abstractmethod
from osgeo import ogr
from osgeo import osr
import numpy as np
from geoalchemy2.elements import WKBElement
from geoalchemy2.shape import from_shape
from shapely import affinity
from shapely.geometry.base import BaseGeometry
import shapely.geometry as shp_geom
from shapely.wkt import loads
from lostservice.geometry import reproject_geom, getutmsrid, calculate_orientation, calculate_arc


class Geodetic2D(object):
    """
    Base class for all geodetic 2D geometries.
    """
    __metaclass__ = ABCMeta

    def __init__(self, spatial_ref: str=None):
        """
        Base constructor for all geodetic 2D geometries.

        :param spatial_ref: The spatial reference identifier (full URN) for the given geometry.
        :type spatial_ref: ``str``
        """
        super(Geodetic2D, self).__init__()
        self._spatial_ref: str = spatial_ref
        self._spatial_ref_id: int = self._trim_srid_urn(spatial_ref) if spatial_ref is not None else None
        self._shapely_internal: BaseGeometry = None

    @property
    def spatial_ref(self) -> str:
        """
        The spatial reference identifier URN.

        :type: ``str``
        """
        return self._spatial_ref

    @spatial_ref.setter
    def spatial_ref(self, value: str) -> None:
        self._spatial_ref = value
        self._spatial_ref_id = self._trim_srid_urn(value)

    @property
    def sr_id(self) -> int:
        """
        The spatial reference id number as an integer.

        :return: ``int``
        """
        return self._spatial_ref_id

    @abstractmethod
    def build_shapely_geometry(self) -> BaseGeometry:
        """
        Builds the internal shapely representation of the geometry.  This is used by other base class methods
        to build the other output types.

        :return: A shapely geometry specific to the derived type.
        :rtype: :py:class:`BaseGeometry`
        """
        pass

    def _trim_srid_urn(self, srid_urn: str) -> int:
        """
        Get's the SRID from the given SR URN.

        :param srid_urn: The spatial reference urn.
        :type srid_urn: ``str``
        :return: The SRID.
        :rtype: ``int``
        """
        return int(srid_urn.split('::')[1])

    def _get_ogr_sr(self, srid: int) -> osr.SpatialReference:
        """
        Get's an OGR SpatialReference for the current object.

        :param srid: The well known SRID.
        :type srid: ``int``
        :return: A SpatialReference instance for the given SRID.
        :rtype: :py:class:`osr.SpatialReference`
        """
        spatial_reference = osr.SpatialReference()
        spatial_reference.ImportFromEPSG(srid)
        return spatial_reference

    def to_ogr_geometry(self, project_to: int=None) -> ogr.Geometry:
        """
        Get the geometry as an ogr Geometry type.

        :return: The OGR geometry.
        :rtype: :py:class:`ogr.Geometry`
        """
        if self._shapely_internal is None:
            self.build_shapely_geometry()

        ogr_geom: ogr.Geometry = ogr.CreateGeometryFromWkt(self._shapely_internal.wkt)
        ogr_geom.AssignSpatialReference(self._get_ogr_sr(self.sr_id))

        if project_to and project_to != self.sr_id:
            ogr_geom = reproject_geom(ogr_geom, self.sr_id, project_to)

        return ogr_geom

    def to_wkbelement(self, project_to: int=None) -> WKBElement:
        """
        Get the geometry as a geoalchemy WKBElement.

        :return: The geometry as a WKBELement.
        :rtype: :py:class:`WKBElement`
        """
        if self._shapely_internal is None:
            self.build_shapely_geometry()

        wkb = None
        if project_to and project_to != self.sr_id:
            ogr_geom: ogr.Geometry = ogr.CreateGeometryFromWkt(self._shapely_internal.wkt)
            ogr_geom.AssignSpatialReference(self._get_ogr_sr(self.sr_id))
            ogr_geom = reproject_geom(ogr_geom, self.sr_id, project_to)
            wkb = from_shape(loads(ogr_geom.ExportToWkt(), project_to))
        else:
            wkb = from_shape(self._shapely_internal, self.sr_id())

        return wkb


class Point(Geodetic2D):
    """
    A class for representing Point geometries.
    """

    def __init__(self, spatial_ref: str=None, lat: float=None, lon: float=None):
        """
        Constructor for Point geometries.

        :param spatial_ref: The spatial reference identifier for the given geometry.
        :type spatial_ref: ``str``
        :param lat: Latitude
        :type lat: ``float``
        :param lon: Longitude
        :type lon: ``float``
        """
        super(Point, self).__init__(spatial_ref)
        self._lat = lat
        self._lon = lon

    @property
    def latitude(self) -> float:
        """
        The latitude.

        :rtype: ``float``
        """
        return self._lat

    @latitude.setter
    def latitude(self, value: float) -> None:
        self._lat = value

    @property
    def longitude(self) -> float:
        """
        The longitude.

        :rtype: ``float``
        """
        return self._lon

    @longitude.setter
    def longitude(self, value: float) -> None:
        self._lon = value

    def build_shapely_geometry(self) -> BaseGeometry:
        """
        Builds the internal shapely representation of the geometry.  This is used by other base class methods
        to build the other output types.

        :return: A shapely geometry specific to the derived type.
        :rtype: :py:class:`BaseGeometry`
        """
        return shp_geom.Point(self.longitude, self.latitude)


class Circle(Geodetic2D):
    """
    A class for representing Circle geometries.
    """

    def __init__(self, spatial_ref: str=None, lat: float=None, lon: float=None, radius: float=None, uom: str=None):
        """
        Constructor for Circle geometries.

        :param spatial_ref: The spatial reference URN.
        :type spatial_ref: ``str``
        :param lat: Latitude
        :type lat: ``float``
        :param lon: Longitude
        :type lon: ``float``
        :param radius: Radius of the circle
        :type radius: ``float``
        :param uom: Unit of measure identifier for the radius.
        :type uom: ``str``
        """
        super(Circle, self).__init__(spatial_ref)
        self._lat = lat
        self._lon = lon
        self._radius = radius
        self._uom = uom

    @property
    def latitude(self) -> float:
        """
        The latitude.

        :rtype: ``float``
        """
        return self._lat

    @latitude.setter
    def latitude(self, value: float):
        self._lat = value

    @property
    def longitude(self):
        """
        The longitude.

        :rtype: ``float``
        """
        return self._lon

    @longitude.setter
    def longitude(self, value):
        self._lon = value

    @property
    def radius(self):
        """
        The radius.

        :rtype: ``float``
        """
        return self._radius

    @radius.setter
    def radius(self, value):
        self._radius = value

    @property
    def uom(self):
        """
        The unit of measure identifier.

        :rtype: ``str``
        """
        return self._uom

    @uom.setter
    def uom(self, value):
        self._uom = value

    def build_shapely_geometry(self) -> BaseGeometry:
        """
        Builds the internal shapely representation of the geometry.  This is used by other base class methods
        to build the other output types.

        :return: A shapely geometry specific to the derived type.
        :rtype: :py:class:`BaseGeometry`
        """
        # Get the UTMSRID so we can transform the center point to a coordinate system where distance is
        # measured in meters.
        utmsrid = getutmsrid(self.longitude, self.latitude, self.sr_id)
        # Create the OGR Point
        center = ogr.Geometry(ogr.wkbPoint)
        center.AddPoint(self.longitude, self.latitude)
        # Project the point from its native projection to the UTM system.
        center = reproject_geom(center, self.sr_id, utmsrid)
        # Buffer the point with the radius to get a polygon of the circle.
        circle = center.Buffer(self.radius)
        # Project the circle back to the original system.
        circle = reproject_geom(circle, utmsrid, self.sr_id)
        # Return a shapely object constructed from the WKT of the OGR polygon
        return loads(circle.ExportToWkt())


class Ellipse(Geodetic2D):
    """
    A class for representing Ellipse geometries.
    """

    def __init__(self, spatial_ref=None, lat=None, lon=None,
                 majorAxis=None, majorAxisuom=None,
                 minorAxis=None, minorAxisuom=None,
                 orinetation=None, orinetationuom=None  ):
        """
        Constructor for Ellipse geometries.

        :param spatial_ref: The spatial reference URN.
        :type spatial_ref: ``str``
        :param lat: Latitude
        :type lat: ``float``
        :param lon: Longitude
        :type lon: ``float``
        :param majorAxis: majorAxis of the Ellipse
        :type majorAxis: ``float``
        :param majorAxisuom: Unit of measure identifier for the majorAxis.
        :type majorAxisuom: ``str``
        :param minorAxis: minorAxis of the Ellipse
        :type minorAxis: ``float``
        :param minorAxisuom: Unit of measure identifier for the minorAxis.
        :type minorAxisuom: ``str``
        :param orinetation: orinetation of the Ellipse
        :type orinetation: ``float``
        :param orinetationuom: Unit of measure identifier for the orinetation.
        :type orinetationuom: ``str``
        """
        super(Ellipse, self).__init__(spatial_ref)
        self._lat = lat
        self._lon = lon
        self._majorAxis = majorAxis
        self._majorAxisuom = majorAxisuom
        self._minorAxis = minorAxis
        self._minorAxisuom = minorAxisuom
        self._orinetation = orinetation
        self._orinetationuom = orinetationuom

    @property
    def latitude(self):
        """
        The latitude.

        :rtype: ``float``
        """
        return self._lat

    @latitude.setter
    def latitude(self, value):
        self._lat = value

    @property
    def longitude(self):
        """
        The longitude.

        :rtype: ``float``
        """
        return self._lon

    @longitude.setter
    def longitude(self, value):
        self._lon = value

    @property
    def majorAxis(self):
        """
        The _majorAxis.

        :rtype: ``float``
        """
        return self.__majorAxis

    @majorAxis.setter
    def majorAxis(self, value):
        self.__majorAxis = value

    @property
    def majorAxisuom(self):
        """
        The unit of measure identifier.

        :rtype: ``str``
        """
        return self.__majorAxisuom

    @majorAxisuom.setter
    def majorAxisuom(self, value):
        self._majorAxisuom = value

    @property
    def minorAxis(self):
        """
        The minorAxis.

        :rtype: ``float``
        """
        return self._minorAxis

    @minorAxis.setter
    def minorAxis(self, value):
        self._minorAxis = value

    @property
    def minorAxisuom(self):
        """
        The unit of measure identifier.

        :rtype: ``str``
        """
        return self._minorAxisuom

    @minorAxisuom.setter
    def minorAxisuom(self, value):
        self._minorAxisuom = value

    @property
    def orinetation(self):
        """
        The orinetation.

        :rtype: ``float``
        """
        return self._orinetation

    @orinetation.setter
    def orinetation(self, value):
        self._orinetation = value

    @property
    def orinetationuom(self):
        """
        The unit of measure identifier.

        :rtype: ``str``
        """
        return self._orinetationuom

    @orinetationuom.setter
    def orinetationuom(self, value):
        self._orinetationuom = value

    def build_shapely_geometry(self) -> BaseGeometry:
        """
        Builds the internal shapely representation of the geometry.  This is used by other base class methods
        to build the other output types.

        :return: A shapely geometry specific to the derived type.
        :rtype: :py:class:`BaseGeometry`
        """
        # Get the UTMSRID so we can transform the center point to a coordinate system where distance is
        # measured in meters.
        utmsrid: int = getutmsrid(self.longitude, self.latitude, self.sr_id)
        # Create the OGR Point
        center: ogr.Geometry = ogr.Geometry(ogr.wkbPoint)
        center.AssignSpatialReference(self.sr_id)
        center.AddPoint(self.longitude, self.latitude)
        # Project the point from its native projection to the UTM system.
        center = reproject_geom(center, self.sr_id, utmsrid)
        # Buffer the point with the radius to get a polygon of the circle.
        circle: ogr.Geometry = center.Buffer(1)

        # Create the shapely object so we can do the ellipse magic.
        proto_ellipse = loads(circle.ExportToWkt())
        # stretch the ellipse along the major and minor axes
        scaled_ellipse = affinity.scale(proto_ellipse, self.majorAxis, self.minorAxis)

        rotate_angle = calculate_orientation(self.orinetation)

        rotated_ellipse = None
        if rotate_angle >= 0:
            # Let rotate the ellipse (clockwise, x axis pointing right):
            rotated_ellipse = affinity.rotate(scaled_ellipse, rotate_angle, use_radians=True)
        else:
            # If one need to rotate it clockwise along an upward pointing x axis:
            rotated_ellipse = affinity.rotate(scaled_ellipse, 90 - rotate_angle, use_radians=True)
            # According to the man, a positive value means a anti-clockwise angle,
            # and a negative one a clockwise angle.

        # Now build an OGR geometry so we can reproject.
        ogr_ellipse: ogr.Geometry = ogr.CreateGeometryFromWkt(rotated_ellipse.wkt)
        ogr_ellipse.AssignSpatialReference(utmsrid)
        ogr_ellipse = reproject_geom(ogr_ellipse, utmsrid, self.sr_id)

        return loads(ogr_ellipse.ExportToWkt())


class Arcband(Geodetic2D):
    """
    A class for representing Arcband geometries.

    """

    def __init__(self, spatial_ref=None, lat=None, lon=None,
                 inner_radius=None, inner_radius_uom=None,
                 outer_radius=None, outer_radios_uom=None,
                 start_angle=None, start_angle_uom=None,
                 opening_angle=None, opening_angle_uom=None):
        """
        Constructor for arcband geometries.

        :param spatial_ref:
        :param lat:
        :param lon:
        :param inner_radius:
        :param inner_radius_uom:
        :param outer_radius:
        :param outer_radios_uom:
        :param start_angle:
        :param start_angle_uom:
        :param opening_angle:
        :param opening_angle_uom:
        """

        super(Arcband, self).__init__(spatial_ref)
        self._lat = lat
        self._lon = lon
        self._inner_radius = inner_radius
        self._inner_radius_uom = inner_radius_uom
        self._outer_radius = outer_radius
        self._outer_radius_uom = outer_radios_uom
        self._start_angle = start_angle
        self._start_angle_uom = start_angle_uom
        self._opening_angle = opening_angle
        self._opening_angle_uom = opening_angle_uom

    @property
    def latitude(self):
        """
        Center point latitude.

        :rtype: ``str``
        """
        return self._lat

    @latitude.setter
    def latitude(self, value):
        self._lat = value

    @property
    def longitude(self):
        """
        Center point longitude.

        :rtype: ``str``
        """
        return self._lon

    @longitude.setter
    def longitude(self, value):
        self._lon = value

    @property
    def inner_radius(self):
        """
        Inner radius.

        :rtype: ``str``
        """
        return self._inner_radius

    @inner_radius.setter
    def inner_radius(self, value):
        self._inner_radius = value

    @property
    def inner_radius_uom(self):
        """
        Inner radius unit of measure.

        :rtype: ``str``
        """
        return self._inner_radius_uom

    @inner_radius_uom.setter
    def inner_radius_uom(self, value):
        self._inner_radius_uom = value

    @property
    def outer_radius(self):
        """
        Outer radius.

        :rtype: ``str``
        """
        return self._outer_radius

    @outer_radius.setter
    def outer_radius(self, value):
        self._outer_radius = value

    @property
    def outer_radius_uom(self):
        """
        Outer radius unit of measure.

        :rtype: ``str``
        """
        return self._outer_radius_uom

    @outer_radius_uom.setter
    def outer_radius_uom(self, value):
        self._outer_radius_uom = value

    @property
    def start_angle(self):
        """
        Start angle in units clockwise from north.

        :rtype: ``str``
        """
        return self._start_angle

    @start_angle.setter
    def start_angle(self, value):
        self._start_angle = value

    @property
    def start_angle_uom(self):
        """
        Start angle units of measure

        :rtype: ``str``
        """
        return self._start_angle_uom

    @start_angle_uom.setter
    def start_angle_uom(self, value):
        self._start_angle_uom = value

    @property
    def opening_angle(self):
        """
        Opening angle in units clockwise from start angle.

        :rtype: ``str``
        """
        return self._opening_angle

    @opening_angle.setter
    def opening_angle(self, value):
        self._opening_angle = value

    @property
    def opening_angle_uom(self):
        """
        Opening angle units of measure

        :rtype: ``str``
        """
        return self._opening_angle_uom

    @opening_angle_uom.setter
    def opening_angle_uom(self, value):
        self._opening_angle_uom = value

    def build_shapely_geometry(self) -> BaseGeometry:
        """
        Builds the internal shapely representation of the geometry.  This is used by other base class methods
        to build the other output types.

        :return: A shapely geometry specific to the derived type.
        :rtype: :py:class:`BaseGeometry`
        """
        # Get the UTMSRID so we can transform the center point to a coordinate system where distance is
        # measured in meters.
        utmsrid: int = getutmsrid(self.longitude, self.latitude, self.sr_id)
        # Create the OGR Point
        center: ogr.Geometry = ogr.Geometry(ogr.wkbPoint)
        center.AssignSpatialReference(self._spatial_ref_id)
        center.AddPoint(self.longitude, self.latitude)
        # Project the point from its native projection to the UTM system.
        center = reproject_geom(center, self._spatial_ref_id, utmsrid)

        # adjust for the fact that we're not doing standard geometry - back up 90 degress
        # to start from north.
        start_angle = 90 - self.start_angle
        # find the end angle, which is the sweep relative to the start angle going clockwise so we subtract.
        end_angle = start_angle - self.opening_angle

        # plot a line for the outer arc.
        outer_arc_x, outer_arc_y = \
            calculate_arc(center.GetX(), center.GetY(), self.outer_radius, start_angle, end_angle)

        # plot a line for the inner arc.
        inner_arc_x, inner_arc_y = \
            calculate_arc(center.GetX(), center.GetY(), self.inner_radius, start_angle, end_angle)

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

        # Build the shapely linear ring . . .
        line_string = shp_geom.LinearRing(ring_coordinates)
        # so we can build a shapely polygon . . .
        arc_band_polygon = shp_geom.Polygon(line_string)
        # so we can create the OGR geometry . . .
        arcband = ogr.CreateGeometryFromWkb(arc_band_polygon.wkb)
        # so we can reproject back to the original coordinate system
        arcband = reproject_geom(arcband, utmsrid, self._spatial_ref_id)
        # so we can build and return a shapely geometry.  (Whew!)
        return loads(arcband.ExportToWkt())


class Polygon(Geodetic2D):
    """
    A class for polygon geometries.
    """
    def __init__(self, spatial_ref=None, vertices=None):
        """
        Constructor.

        :param spatial_ref: The spatial reference identifier for the given geometry.
        :type spatial_ref: ``str``
        :param vertices: The vertices that make up the polygon.
        :type vertices: ``list``
        """
        super(Polygon, self).__init__(spatial_ref)
        self._vertices = vertices if vertices is not None else []

    @property
    def vertices(self):
        """
        The vertices of the polygon.

        :return: ``list``
        """
        return self._vertices

    @vertices.setter
    def vertices(self, value):
        self._vertices = value

    def build_shapely_geometry(self) -> BaseGeometry:
        """
        Builds the internal shapely representation of the geometry.  This is used by other base class methods
        to build the other output types.

        :return: A shapely geometry specific to the derived type.
        :rtype: :py:class:`BaseGeometry`
        """
        return shp_geom.LinearRing(self.vertices)
