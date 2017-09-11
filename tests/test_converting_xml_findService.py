#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import unittest

from lxml import etree

from lostservice.converting.xml import FindServiceXmlConverter


class FindServiceTest(unittest.TestCase):
    def test_findservice_civic_address(self):
        """
        Basic test for findService parsing with a civic address.

        """

        xml = """
            <findService xmlns="urn:ietf:params:xml:ns:lost1" serviceBoundary="reference">
                <location id="ce152f4b-2ade-4e37-9741-b6649e2d87a6" profile="civic">
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
                <service>urn:nena:service:sos</service>
            </findService>
            """

        root = etree.fromstring(xml)

        target = FindServiceXmlConverter()
        result = target.parse(root)

        self.assertEqual(result.location.id, 'ce152f4b-2ade-4e37-9741-b6649e2d87a6')


if __name__ == '__main__':
    unittest.main()
