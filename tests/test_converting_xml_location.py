#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import unittest

from lxml import etree

from lostservice.converting.xml import LocationXmlConverter


class LocationTest(unittest.TestCase):
    def test_location_civic_address(self):
        """
        Basic test for civic address parsing within the location element.
        
        :return: 
        """
        xml_path = os.path.join(os.path.dirname(__file__), './converting/location_civic.xml')
        doc = etree.parse(xml_path)
        root = doc.getroot()
        target = LocationXmlConverter()
        result = target.parse(root)
        self.assertEquals(result.id, 'ce152f4b-2ade-4e37-9741-b6649e2d87a6')
        self.assertEquals(result.profile, 'civic')
        self.assertEquals(result.civic_address.country, 'US')
        self.assertEquals(result.civic_address.a1, 'ME')
        self.assertEquals(result.civic_address.a2, 'Piscataquis')
        self.assertEquals(result.civic_address.a3, 'T3 R11 Wels')
        self.assertEquals(result.civic_address.rd, 'Golden')
        self.assertEquals(result.civic_address.sts, 'Rd')
        self.assertEquals(result.civic_address.hno, '5833')
        self.assertEquals(result.civic_address.pc, '00135')

    def test_location_circle(self):
        """
        Basic test for parsing a circle geometry in a location element.
        
        :return: 
        """
        xml_path = os.path.join(os.path.dirname(__file__), './converting/location_circle.xml')
        doc = etree.parse(xml_path)
        root = doc.getroot()
        target = LocationXmlConverter()
        result = target.parse(root)
        self.assertEquals(result.id, '24b276e1-7eca-48d5-be24-30e0dd4c1ca0')
        self.assertEquals(result.profile, 'geodetic-2d')
        self.assertEquals(result.geodetic2d.spatial_ref, 'urn:ogc:def:crs:EPSG::4326')
        self.assertEquals(result.geodetic2d.latitude, 45.4430670070877)
        self.assertEquals(result.geodetic2d.longitude, -68.4977255651657)
        self.assertEquals(result.geodetic2d.uom, 'urn:ogc:def:uom:EPSG::9001')
        self.assertEquals(result.geodetic2d.radius, '6105.41237061098')


if __name__ == '__main__':
    unittest.main()