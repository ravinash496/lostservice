#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import unittest

from lxml import etree

from lostservice.converting.xml import CircleXmlConverter


class CircleTest(unittest.TestCase):

    def test_basic_circle(self):
        """
        Basic test for circle parsing.
        :return: 
        """
        xml = """
            <gs:Circle xmlns:gs="http://www.opengis.net/pidflo/1.0" xmlns:gml="http://www.opengis.net/gml"
                xmlns="urn:ietf:params:xml:ns:lost1" srsName="urn:ogc:def:crs:EPSG::4326">
                <gml:pos>45.4430670070877 -68.4977255651657</gml:pos>
                <gs:radius uom="urn:ogc:def:uom:EPSG::9001">6105.41237061098</gs:radius>
            </gs:Circle>
            """

        root = etree.fromstring(xml)
        target = CircleXmlConverter()
        result = target.parse(root)
        self.assertEqual(result.spatial_ref, 'urn:ogc:def:crs:EPSG::4326')
        self.assertEqual(result.latitude, 45.4430670070877)
        self.assertEqual(result.longitude, -68.4977255651657)
        self.assertEqual(result.uom, 'urn:ogc:def:uom:EPSG::9001')
        self.assertEqual(result.radius, '6105.41237061098')


if __name__ == '__main__':
    unittest.main()
