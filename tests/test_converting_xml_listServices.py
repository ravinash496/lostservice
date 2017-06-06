#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from lxml import etree
from lostservice.converting.xml import ListServicesXmlConverter
from lostservice.model.responses import ListServicesResponse

LOST_URN = 'urn:ietf:params:xml:ns:lost1'


class TestListServicesConverting(unittest.TestCase):
    
    def test_parse_request(self):
        basic_request = """
        <listServices xmlns="urn:ietf:params:xml:ns:lost1">  
            <service>urn:service:sos</service>
        </listServices>
        """
        root = etree.fromstring(basic_request)
        target = ListServicesXmlConverter()
        result = target.parse(root)
        self.assertEqual(result.service, 'urn:service:sos')

    def test_parse_request_no_service(self):
        basic_request = """
        <listServices xmlns="urn:ietf:params:xml:ns:lost1">  
        </listServices>
        """
        root = etree.fromstring(basic_request)
        target = ListServicesXmlConverter()
        result = target.parse(root)
        self.assertIsNone(result.service)

    def test_format_response(self):
        response = ListServicesResponse()
        response.services = ['service1', 'service2', 'service3']
        response.path = ['path1', 'path2']
        target = ListServicesXmlConverter()
        result = target.format(response)

        services = result.xpath('./serviceList/text()', namespaces={'lost': LOST_URN})
        self.assertIsNotNone(services)
        self.assertEqual(services, ['service1 service2 service3'])
        path = result.xpath('path', namespaces={'lost': LOST_URN})
        self.assertIsNotNone(path)
        self.assertEqual(len(path[0]), 2)

    def test_format_response_nopath(self):
        response = ListServicesResponse()
        response.services = ['service1', 'service2', 'service3']
        target = ListServicesXmlConverter()
        result = target.format(response)

        services = result.xpath('./serviceList/text()', namespaces={'lost': LOST_URN})
        self.assertIsNotNone(services)
        self.assertEqual(services, ['service1 service2 service3'])


if __name__ == '__main__':
    unittest.main()