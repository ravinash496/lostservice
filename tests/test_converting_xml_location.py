#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import unittest

from lxml import etree

from lostservice.converting.xml import LocationXmlConverter
from lostservice.model.location import LocationType


class LocationTest(unittest.TestCase):
    def test_location_civic_address(self):
        """
        Basic test for civic address parsing within the location element.
        
        """

        xml = """
            <location xmlns="urn:ietf:params:xml:ns:lost1" id="ce152f4b-2ade-4e37-9741-b6649e2d87a6" profile="civic">
                <civ:civicAddress xmlns:civ="urn:ietf:params:xml:ns:pidf:geopriv10:civicAddr">
                    <civ:country>US</civ:country>
                    <civ:A1>ME</civ:A1>
                    <civ:A2>Piscataquis</civ:A2>
                    <civ:A3>T3 R11 Wels</civ:A3>
                    <civ:RD>Golden</civ:RD>
                    <civ:STS>Rd</civ:STS>
                    <civ:HNO>5833</civ:HNO>
                    <civ:PC>00135</civ:PC>
                </civ:civicAddress>
            </location>
            """

        root = etree.fromstring(xml)

        target = LocationXmlConverter()
        result = target.parse(root)
        self.assertEquals(result.id, 'ce152f4b-2ade-4e37-9741-b6649e2d87a6')
        self.assertEquals(result.profile, 'civic')
        self.assertEquals(result.location.country, 'US')
        self.assertEquals(result.location.a1, 'ME')
        self.assertEquals(result.location.a2, 'Piscataquis')
        self.assertEquals(result.location.a3, 'T3 R11 Wels')
        self.assertEquals(result.location.rd, 'Golden')
        self.assertEquals(result.location.sts, 'Rd')
        self.assertEquals(result.location.hno, '5833')
        self.assertEquals(result.location.pc, '00135')
        self.assertTrue(result.location_type is LocationType.CIVIC)

    def test_location_circle(self):
        """
        Basic test for parsing a circle geometry in a location element.
        
        """

        xml = """
            <location xmlns="urn:ietf:params:xml:ns:lost1" id="24b276e1-7eca-48d5-be24-30e0dd4c1ca0" profile="geodetic-2d">
                <gs:Circle xmlns:gs="http://www.opengis.net/pidflo/1.0" xmlns:gml="http://www.opengis.net/gml" srsName="urn:ogc:def:crs:EPSG::4326">
                    <gml:pos>45.4430670070877 -68.4977255651657</gml:pos>
                    <gs:radius uom="urn:ogc:def:uom:EPSG::9001">6105.41237061098</gs:radius>
                </gs:Circle>
            </location>
            """

        root = etree.fromstring(xml)

        target = LocationXmlConverter()
        result = target.parse(root)
        self.assertEquals(result.id, '24b276e1-7eca-48d5-be24-30e0dd4c1ca0')
        self.assertEquals(result.profile, 'geodetic-2d')
        self.assertEquals(result.location.spatial_ref, 'urn:ogc:def:crs:EPSG::4326')
        self.assertEquals(result.location.latitude, 45.4430670070877)
        self.assertEquals(result.location.longitude, -68.4977255651657)
        self.assertEquals(result.location.uom, 'urn:ogc:def:uom:EPSG::9001')
        self.assertEquals(result.location.radius, '6105.41237061098')
        self.assertTrue(result.location_type is LocationType.GEODETIC2D)


if __name__ == '__main__':
    unittest.main()