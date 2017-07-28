#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import unittest

from lxml import etree

from lostservice.converting.xml import ArcbandXmlConverter


class ArcbandTest(unittest.TestCase):

    def test_basic_arcband(self):
        """
        Basic test for arcband parsing.
        :return:
        """
        xml = """
            <gs:ArcBand srsName="urn:ogc:def:crs:EPSG::4326" 
                        xmlns:gs="http://www.opengis.net/pidflo/1.0"
                        xmlns:gml="http://www.opengis.net/gml">
                <gml:pos>42.5463 -73.2512</gml:pos>
                <gs:innerRadius uom="urn:ogc:def:uom:EPSG::9001">1661.55</gs:innerRadius>
                <gs:outerRadius uom="urn:ogc:def:uom:EPSG::9001">2215.4</gs:outerRadius>
                <gs:startAngle uom="urn:ogc:def:uom:EPSG::9102">266</gs:startAngle>
                <gs:openingAngle uom="urn:ogc:def:uom:EPSG::9102">120</gs:openingAngle>
            </gs:ArcBand>
            """

        root = etree.fromstring(xml)
        target = ArcbandXmlConverter()
        result = target.parse(root)
        self.assertEqual(result.spatial_ref, 'urn:ogc:def:crs:EPSG::4326')
        self.assertEqual(result.latitude, 42.5463)
        self.assertEqual(result.longitude, -73.2512)
        self.assertEqual(result.inner_radius, 1661.55)
        self.assertEqual(result.inner_radius_uom, 'urn:ogc:def:uom:EPSG::9001')
        self.assertEqual(result.outer_radius, 2215.4)
        self.assertEqual(result.outer_radius_uom, 'urn:ogc:def:uom:EPSG::9001')
        self.assertEqual(result.start_angle, 266)
        self.assertEqual(result.start_angle_uom, 'urn:ogc:def:uom:EPSG::9102')
        self.assertEqual(result.opening_angle, 120)
        self.assertEqual(result.opening_angle_uom, 'urn:ogc:def:uom:EPSG::9102')


if __name__ == '__main__':
    unittest.main()
