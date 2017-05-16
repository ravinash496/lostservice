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
        xml_path = os.path.join(os.path.dirname(__file__), 'basic_civic_address.xml')
        doc = etree.parse(xml_path)
        root = doc.getroot()

        target = CivicXmlConverter()
        result = target.parse(root)
        self.assertEquals(result.country, 'US')
        self.assertEquals(result.a1, 'ME')
        self.assertEquals(result.a2, 'Piscataquis')
        self.assertEquals(result.a3, 'T3 R11 Wels')
        self.assertEquals(result.rd, 'Golden')
        self.assertEquals(result.sts, 'Rd')
        self.assertEquals(result.hno, '5833')
        self.assertEquals(result.pc, '00135')


if __name__ == '__main__':
    unittest.main()