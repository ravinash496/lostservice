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
        xml_path = os.path.join(os.path.dirname(__file__), 'circle.xml')
        doc = etree.parse(xml_path)
        root = doc.getroot()
        target = CircleXmlConverter()
        result = target.parse(root)
        self.assertEquals(result.spatial_ref, 'urn:ogc:def:crs:EPSG::4326')
        self.assertEquals(result.latitude, 45.4430670070877)
        self.assertEquals(result.longitude, -68.4977255651657)
        self.assertEquals(result.uom, 'urn:ogc:def:uom:EPSG::9001')
        self.assertEquals(result.radius, '6105.41237061098')


if __name__ == '__main__':
    unittest.main()
