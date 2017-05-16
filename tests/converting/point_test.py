#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import unittest

from lxml import etree

from lostservice.converting.xml import PointXmlConverter


class PointTest(unittest.TestCase):
    def test_basic_point(self):
        """
        Basic test for point parsing.
        :return: 
        """
        xml_path = os.path.join(os.path.dirname(__file__), 'point.xml')
        doc = etree.parse(xml_path)
        root = doc.getroot()

        target = PointXmlConverter()
        result = target.parse(root)
        self.assertEquals(result.spatial_ref, 'urn:ogc:def:crs:EPSG::4326')
        self.assertEquals(result.latitude, 45.4524048105657)
        self.assertEquals(result.longitude, -68.5452615106889)


if __name__ == '__main__':
    unittest.main()
