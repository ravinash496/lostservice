#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. currentmodule:: lostservice.geometryutility
.. moduleauthor:: Pat Blair <pblair@geo-comm.com>
.. currently a copy of civvy's GeometryUtility.

Implementation classes for findservice queries.
"""
from enum import Enum

from geoalchemy2.shape import to_shape
from measurement.measures import Distance
from osgeo import ogr
from shapely.geometry.base import BaseGeometry
from shapely.geometry.point import Point
from shapely.geometry.linestring import LineString
from typing import Dict

import re
import shapely.wkb



class Sides(Enum):
    """
    This is a simple enumeration that identifies the side of centerline (left or right).
    """
    LEFT = 'left'    #: the left side
    RIGHT = 'right'  #: the right side


class GeometryUtility(object):
    """
    Use a geometry utility instance to make working with geometries a little easier.
    """
    # This is a regex that matches an EWKT string, capturing the spatial reference ID (SRID) in a group called 'srid'
    # and the rest of the well-known text (WKT) in a group called 'wkt'.
    _ewkt_re = re.compile(
        r"srid=(?P<srid>\d+)\s*;\s*(?P<wkt>.*)",
        flags=re.IGNORECASE)  #: a regex that matches extended WKT (EWKT)

    def __init__(self,
                 projected_srid: int=3857):
        """

        :param projected_srid: the SRID of the projected coordinate system used by this utility
        :type projected_srid:  ``int``
        """
        # Create the cache of manufactured spatial references (so we don't have to keep creating them over and over.)
        self._spatial_references: Dict[int, ogr.osr.SpatialReference] = {}
        self._projected_srid = projected_srid  #: the SRID of the projected coordinate system used by this utility
        self._projected_srs = ogr.osr.SpatialReference()  #: the projected coordinate system used by this utility
        # Import the projected spatial reference.
        self._projected_srs.ImportFromEPSG(self._projected_srid)

    def get_spatial_reference(self, srid: int) -> ogr.osr.SpatialReference:
        """
        Get the spatial reference associated with an SRID.

        :param srid:  the spatial reference identifier
        :type srid:  :py:class:`ogr.osr.SpatialReference`
        :return: the associated spatial reference
        :rtype:  :py:class:`ogr.osr.SpatialReference`
        """
        # If we've already created a spatial reference...
        if srid in self._spatial_references:
            # ...return it to the caller.
            return self._spatial_references[srid]
        else:  # Otherwise, it's time to build this one.
            srs = ogr.osr.SpatialReference()
            srs.ImportFromEPSG(srid)
            # Save this spatial reference (so we don't need to create it again).
            self._spatial_references[srid] = srs
            # Now we can return it.
            return srs

    def get_srid(self, geometry: ogr.Geometry) -> int or None:
        """
        Get the SRID of an OGR geometry's spatial reference

        :param geometry: the geometry
        :type geometry:  :py:class:`ogr.Geometry`
        :return: the SRID (or ``None`` if the geometry has no spatial reference)
        :rtype:  ``int`` or ``None``
        """
        # Get the spatial reference.
        srs: ogr.osr.SpatialReference = geometry.GetSpatialReference()
        # If the geometry has no spatial reference, return None to the caller.
        if srs is None:
            return None
        else:
            # Dig out the SRID.
            # https://gis.stackexchange.com/questions/20298/is-it-possible-to-get-the-epsg-value-from-an-osr-spatialreference-class-using-th
            srid = int(srs.GetAttrValue('AUTHORITY', 1))
            return srid

    def create_geometry_from_ewkt(self, ewkt: str) -> ogr.Geometry:
        """
        Create an OGR geometry from an extended WKT (EWKT) string.

        :param ewkt: the extended WKT (EWKT) string representation
        :param wkt:  ``str``
        :return: the geometry
        :rtype:  :py:class:`ogr.Geometry`
        """
        # Let's try to match the format so we can separate the SRID from the rest of the WKT.
        ewkt_match = self._ewkt_re.search(ewkt)
        if not ewkt_match:
            raise GeometryException('The EWK is not propertly formatted.')  # TODO: Add more information?
        # Great!  The format matched!!  Let's get the pieces.
        srid = int(ewkt_match.group('srid'))  # Grab the SRID.
        wkt = ewkt_match.group('wkt')  # Get the WKT.
        # Now we have everything we need to create an OGR geometry!
        geometry: ogr.Geometry = ogr.CreateGeometryFromWkt(wkt)
        srs: ogr.osr.SpatialReference = self.get_spatial_reference(srid)
        geometry.AssignSpatialReference(srs)
        # Return the geometry!
        return geometry

    def project(self,
                geometry: ogr.Geometry,
                srs: int or ogr.osr.SpatialReference,
                copy: bool=True) -> ogr.Geometry:
        """
        Project a geometry to a spatial reference.

        :param geometry: the geometry to project
        :type geometry:  :py:class:`ogr.Geometry`
        :param srs: the spatial reference (or SRID) to which we're going to project
        :type srs:  :py:class:`ogr.osr.SpatialReference` or ``int``
        :param copy: Make a copy of the geometry or modify the current one?
        :type copy:  ``bool``
        :return: the projected geometry
        :rtype:  :py:class:`ogr.Geometry`
        """
        # The incoming spatial reference argument might be spatial reference, or it might be an SRID.  Figure out
        # which one we're dealing with and make sure we end up with a spatial reference.
        _srs = srs if isinstance(srs, ogr.osr.SpatialReference) else self.get_spatial_reference(srid=srs)
        # The object we ultimately transform depends on the 'copy' parameter.
        _geometry = geometry if not copy else geometry.Clone()
        # Perform the transformation.
        _geometry.TransformTo(_srs)
        # Return whatever we have.
        return _geometry

    def get_parallel_offset(self,
                            linestring: ogr.Geometry,
                            side: Sides,
                            distance: Distance) -> ogr.Geometry:
        """
        Get a linestring geometry that is parallel to a given linestring.

        :param linestring: the linestring for which you want a parallel linestring
        :type linestring:  :py:class:`ogr.Geometry`
        :param side: Which side of the line should the parallel line fall on?
        :type side:  :py:class:`Sides`
        :param distance: How far should the parallel linestring be from the original linestring?
        :type distance:  :py:class:`Distance`
        :return: the parallel linestring
        :rtype:  :py:class:`ogr.Geometry`
        """
        # TODO: This method is a target for performance improvements.  Right now we are switching back and forth between OGR and Shapely geometries a couple of times.
        # Make not of the geometry argument's SRID.  (We'll need it a few times below.)
        _original_srid = self.get_srid(geometry=linestring)
        # If the incoming geometry is in a projected coordinate system that uses meters, we can use it directly.
        # Otherwise, we need to make a copy and transform the copy.
        _linestring = (linestring if _original_srid == self._projected_srid
                       else self.project(geometry=linestring, srs=self._projected_srs, copy=True))
        # Now we need to convert the distance to the units of the projected coordinate system.
        # (See http://python-measurement.readthedocs.io/en/latest/topics/measures.html#distance)
        offset_distance_in_meters = distance.m
        # For our next trick, we'll need a Shapely geometry.
        shapely_linestring: LineString = self.ogr_to_shapely(_linestring)
        # The shapely call takes string values for the 'side' parameter.  Let's figure out what we're going to use.
        side_arg = 'left' if side == Sides.LEFT else 'right'
        # Now we have enough information to use the Shapely parallel_offset() function.
        # (http://toblerity.org/shapely/shapely.geometry.html)
        shapely_linestring_offset = shapely_linestring.parallel_offset(distance=offset_distance_in_meters,
                                                                       side=side_arg,
                                                                       resolution=16,
                                                                       join_style=1,
                                                                       mitre_limit=1.0)
        # Now we convert back to an OGR geometry.
        ogr_linestring_offset = self.shapely_to_ogr(shapely_geometry=shapely_linestring_offset, srs=self._projected_srs)
        # If we projected the original geometry, we need to project it back to the original coordinate system.
        if _original_srid != self._projected_srid:
            ogr_linestring_offset = self.project(geometry=ogr_linestring_offset,
                                                 srs=linestring.GetSpatialReference(),
                                                 copy=False)
        # OK.  That's that.
        return ogr_linestring_offset

    def get_point_at_percent(self,
                             linestring: LineString,
                             pct_along: float,
                             offset_side: Sides=None,
                             offset_distance: Distance=None):
        """
        Get the point on a linestring at a given distance (expressed as a percentage of the total distance) from the
        start of the line.

        :param linestring: the linestring
        :type linestring:  :py:class:`ogr.Geometry`
        :param pct_along: How far along the linestring is the point you want?
        :type pct_along:  ``float``
        :param offset_side: If you want a point on the left- or right-hand side, specify the side.
        :type offset_side:  :py:class:`Sides`
        :param offset_distance: If you want a point offset from the centerline, how far away should it be?
        :type offset_distance:  :py:class:`Distance`
        :return: the point at the specified offset
        :rtype:  :py:class:`ogr.Geometry`
        """
        # Perform a sanity check:  We need the geometry to be a linestring.
        if linestring.GetGeometryType() != ogr.wkbLineString:
            raise GeometryException('The input geometry must be a LineString.')
        # If we haven't been supplied enough information to find an offset, we can just carry on with the original
        # geometry; otherwise we need to find the line parallel on the requested side at the specified distance.
        _linestring = (linestring if offset_side is None or offset_distance is None
                       else self.get_parallel_offset(linestring=linestring,
                                                     side=offset_side,
                                                     distance=offset_distance))
        # Convert the OGR geometry to a shapely geometry so we can perform some calculations.
        shapely_linestring: LineString = self.ogr_to_shapely(_linestring)
        # Let's get the point at the given percent.
        # (See http://toblerity.org/shapely/manual.html#object.interpolate)
        shapely_point_at_pct: Point = shapely_linestring.interpolate(pct_along, normalized=True)
        # Now we need to convert the geometry back to OGR.  (For the spatial reference, we just use the one from the
        # original geometry.)
        ogr_point: ogr.Geometry = self.shapely_to_ogr(shapely_geometry=shapely_point_at_pct,
                                                      srs=linestring.GetSpatialReference())
        # Good to go!
        return ogr_point

    def shapely_to_ogr(self,
                       shapely_geometry: BaseGeometry,
                       srs: int or ogr.osr.SpatialReference) -> ogr.Geometry:
        """
        Convert a Shapely geometry to a GDAL/OGR geometry.

        :param shapely_geometry: the shapely geometry
        :type shapely_geometry:  :py:class:`BaseGeometry`
        :param srs: the spatial reference (or SRID) of the geometry
        :type srs:  :py:class:`SpatialReference` or ``int``
        :return: an OGR geometry
        :rtype:  :py:class:`ogr.Geometry`
        """
        # Perform the WKB->OGR Geometry conversion.
        ogr_geometry: ogr.Geometry = ogr.CreateGeometryFromWkb(shapely_geometry.wkb)
        # Now we need to assign the spatial reference to the geometry (if it isn't already assigned).
        if srs is not None:
            # The caller may have supplied an OGR spatial reference, or the SRID.  If it's the latter, we need to
            # convert it to a spatial reference.
            _srs = srs if isinstance(srs, ogr.osr.SpatialReference) else self.get_spatial_reference(srs)
            # OK.  Now we can assign it.
            ogr_geometry.AssignSpatialReference(_srs)
        # That's that!
        return ogr_geometry

    def ogr_to_shapely(self, ogr_geometry: ogr.Geometry) -> BaseGeometry:
        """
        Convert an OGR geometry to a Shapely geometry.

        :param ogr_geometry: the OGR geometry
        :type ogr_geometry:  :py:class:`ogr.Geometry`
        :return: the base geometry
        :rtype:  :py:class:`BaseGeometry`
        """
        wkb = ogr_geometry.ExportToWkb()
        shapely_geometry = shapely.wkb.loads(wkb)
        return shapely_geometry

    def simplify_polygon(self, mapping_object, tolerance: float):
        """
        Simplify a polygon, generally used when returning service boundaries to lighten to package
        being sent in the response.
        This is THE LAST step after all queries are ran, to keep us in memory for better performance.
        :param object: results object to simplify service boundary geometry from.
        :type object: object
        :param tolerance: the range at which we create the buffer from and simplify off of.
        :type tolerance: float
        :return: same results object, but with simplified service boundary.
        :rtype:
        """
        # First we take the wkb_geometry item of our results object and turn it into a shapely geometry.
        # We only do this, to get the wkb, and then re-transform it back into an ogr geometry.
        # It's very silly, but it's the only way.. for now.

        if mapping_object['wkb_geometry'] is None:
            return mapping_object

        shapely_geometry = to_shape(mapping_object['wkb_geometry'])

        # Also, we add a definitive WKID to the geometry
        my_ogr_geometry = self.shapely_to_ogr(shapely_geometry, 4326)

        # change projected to 3857, then simplify the polygon.
        ogr_reprojected = self.project(my_ogr_geometry, 3857)
        # The buffer is the negative of our tolerance level to "shrink" the original boundary.
        # This guarantees us that when we simplify it, it all fits inside the original boundary.
        ogr_buffered = ogr_reprojected.Buffer(-tolerance)
        ogr_simplified = ogr_buffered.Simplify(tolerance)

        # now that we've simplified, we will want to project back to WKID: 4326
        ogr_wgs_84 = self.project(ogr_simplified, 4326)
        # Geesh, we're not done yet! Let's take this pretty geometry and export it to GML.
        ogr_as_gml = ogr_wgs_84.ExportToGML(options=['FORMAT=GML3'])

        #Wait, all of this actually worked? Well I suppose we should put it into the return object then.
        mapping_object['ST_AsGML_1'] = ogr_as_gml
        # WE OUTTA HERE!
        return mapping_object
