#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import unittest

from lxml import etree

from lostservice.converting.xml import CivicXmlConverter


class CivicTest(unittest.TestCase):
    def test_basic_civic_address(self):
        """
        Basic test for civic address parsing.
        :return: 
        """

        xml = """
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
            """

        root = etree.fromstring(xml)

        target = CivicXmlConverter()
        result = target.parse(root)
        self.assertEqual(result.country, 'US')
        self.assertEqual(result.a1, 'ME')
        self.assertEqual(result.a2, 'Piscataquis')
        self.assertEqual(result.a3, 'T3 R11 Wels')
        self.assertEqual(result.rd, 'Golden')
        self.assertEqual(result.sts, 'Rd')
        self.assertEqual(result.hno, '5833')
        self.assertEqual(result.pc, '00135')


if __name__ == '__main__':
    unittest.main()