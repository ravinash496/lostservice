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
        """

        xml = """
            <gml:Point xmlns:gml="http://www.opengis.net/gml" xmlns="urn:ietf:params:xml:ns:lost1" srsName="urn:ogc:def:crs:EPSG::4326">
                <gml:pos>45.4524048105657 -68.5452615106889</gml:pos>
            </gml:Point>
            """
        root = etree.fromstring(xml)

        target = PointXmlConverter()
        result = target.parse(root)
        self.assertEqual(result.spatial_ref, 'urn:ogc:def:crs:EPSG::4326')
        self.assertEqual(result.latitude, 45.4524048105657)
        self.assertEqual(result.longitude, -68.5452615106889)


if __name__ == '__main__':
    unittest.main()
