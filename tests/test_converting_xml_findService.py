#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import unittest

from lxml import etree

from lostservice.converting.xml import FindServiceXmlConverter


class FindServiceTest(unittest.TestCase):
    def test_findservice_civic_address(self):
        """
        
        :return: 
        """
        xml_path = os.path.join(os.path.dirname(__file__), './converting/findService_civic.xml')
        doc = etree.parse(xml_path)
        root = doc.getroot()

        target = FindServiceXmlConverter()
        result = target.parse(root)

        self.assertEquals(result.location.id, 'ce152f4b-2ade-4e37-9741-b6649e2d87a6')


if __name__ == '__main__':
    unittest.main()