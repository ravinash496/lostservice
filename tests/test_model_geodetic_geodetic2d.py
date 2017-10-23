#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from unittest.mock import patch
from unittest.mock import MagicMock
from lostservice.model.geodetic import Geodetic2D
from shapely.geometry import Point
from osgeo import ogr
from osgeo import osr
from geoalchemy2.elements import WKBElement


class Geodetic2DTest(unittest.TestCase):

    def test_sr_id(self):
        class GeoSub(Geodetic2D):
            def build_shapely_geometry(self):
                pass

        srid_urn = 'urn:ogc:def:crs:EPSG::4326'

        target: GeoSub = GeoSub(srid_urn)
        self.assertEqual(target.spatial_ref, srid_urn)
        self.assertEqual(target.sr_id, 4326)

    def test_to_ogr_geom_no_reproject(self):
        class GeoSub(Geodetic2D):
            def build_shapely_geometry(self):
                return Point(0.0, 1.1)

        srid_urn: str = 'urn:ogc:def:crs:EPSG::4326'

        target: GeoSub = GeoSub(srid_urn)

        actual: ogr.Geometry = target.to_ogr_geometry()
        actual_sr: osr.SpatialReference = actual.GetSpatialReference()
        self.assertEqual(actual.GetX(), 0.0)
        self.assertEqual(actual.GetY(), 1.1)
        self.assertEqual(actual_sr.GetAttrValue('geogcs'), 'WGS 84')

    def test_to_ogr_geom_reproject(self):
        class GeoSub(Geodetic2D):
            def build_shapely_geometry(self):
                return Point(0.0, 1.1)

        srid_urn: str = 'urn:ogc:def:crs:EPSG::4326'

        target: GeoSub = GeoSub(srid_urn)

        actual: ogr.Geometry = target.to_ogr_geometry(project_to=2163)
        actual_sr: osr.SpatialReference = actual.GetSpatialReference()
        self.assertNotEqual(actual.GetX(), 0.0)
        self.assertNotEqual(actual.GetY(), 1.1)
        self.assertEqual(
            actual_sr.GetAttrValue('geogcs'), 'Unspecified datum based upon the Clarke 1866 Authalic Sphere')

    def test_to_wkb_element_no_reproject(self):
        class GeoSub(Geodetic2D):
            def build_shapely_geometry(self):
                return Point(0.0, 1.1)

        srid_urn: str = 'urn:ogc:def:crs:EPSG::4326'
        target: GeoSub = GeoSub(srid_urn)
        actual: WKBElement = target.to_wkbelement()
        self.assertEqual(actual.srid, 4326)

    def test_to_wkb_element_no_reproject(self):
        class GeoSub(Geodetic2D):
            def build_shapely_geometry(self):
                return Point(0.0, 1.1)

        srid_urn: str = 'urn:ogc:def:crs:EPSG::4326'
        target: GeoSub = GeoSub(srid_urn)
        actual: WKBElement = target.to_wkbelement(project_to=2163)
        self.assertEqual(actual.srid, 2163)






