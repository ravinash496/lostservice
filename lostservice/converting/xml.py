#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: lostservice.converting.xml
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

Xml conversion classes.
"""

from lxml import etree
import lxml
from lostservice.converter import Converter
from lostservice.model.location import CivicAddress
from lostservice.model.location import Circle
from lostservice.model.location import Point
from lostservice.model.location import Location
from lostservice.model.requests import FindServiceRequest
from lostservice.model.requests import ListServicesRequest

LOST_PREFIX = 'lost'
LOST_URN = 'urn:ietf:params:xml:ns:lost1'
CIVIC_ADDRESS_PREFIX = 'civ'
CIVIC_ADDRESS_URN = 'urn:ietf:params:xml:ns:pidf:geopriv10:civicAddr'
PIDFLO_PREFIX = 'gs'
PIDFLO_URN = 'http://www.opengis.net/pidflo/1.0'
GML_PREFIX = 'gml'
GML_URN = 'http://www.opengis.net/gml'
CAN_PREFIX = 'can'
CAN_URN = 'urn:nena:xml:ns:pidf:nenaCivicAddr'
CAE_PREFIX = 'cae'
CAE_URN = 'urn:ietf:params:xml:ns:pidf:geopriv10:civicAddr:ext'


_namespace_map = {LOST_PREFIX: LOST_URN,
                  CIVIC_ADDRESS_PREFIX: CIVIC_ADDRESS_URN,
                  PIDFLO_PREFIX: PIDFLO_URN,
                  GML_PREFIX: GML_URN,
                  CAN_PREFIX: CAN_URN,
                  CAE_PREFIX: CAE_URN}


class XmlConverter(Converter):
    """ 
    Base class for all types of XML converters.
    """
    def __init__(self):
        super(XmlConverter, self).__init__()

    def _run_xpath(self, node, xpath):
        """
        Gets the content of a child of the given element.  If the search returns multiple matches, 
         only the first will be used.
         
        :param node: The node from which the search will be initiated. 
        :type node: ``_ElementTree``
        :param xpath: An xpath which selects the desired element.
        :type xpath: ``str``
        :return: The result of the xpath expression.
        :rtype: Depends on the given xpath.
        """
        retval = None
        if node is None or xpath is None:
            raise ValueError('Invalid parameter')

        child = node.xpath(xpath, namespaces=_namespace_map)

        if child:
            retval = child[0]

        return retval

    def parse(self, data):
        """
        Abstract method for message parsing to be implemented by subclasses.

        :param data: The data to be parsed. 
        :return: An instance of type corresponding to the input data.
        """
        raise NotImplementedError('The parse method must be implemented in a subclass.')

    def format(self, data):
        """
        Abstract method for message formatting to be implemented by subclasses.

        :param data: The data to be formatted.
        :return: The formatted output.
        """
        raise NotImplementedError('The format method must be implemented in a subclass.')


class CivicXmlConverter(XmlConverter):
    """
    Implementation class for converting civic addresses from/to XML.
    """
    def __init__(self):
        """
        Constructs a new CivicXmlParser instance.
        
        :return CivicXmlParser: A new CivicXmlParser instance.
        """
        super(CivicXmlConverter, self).__init__()

    def parse(self, data):
        """
        Parse a node containing a civic address.
        
        :param data: The civic address node.
        :type data: :py:class:`_ElementTree`
        :return: A CivicAddress instance.
        :rtype: :py:class:`CivicAddress`
        """
        xpath_template = './{0}:{1}/text()'

        # TODO: use a dictionary
        civic = CivicAddress()
        civic.country = self._run_xpath(data, xpath_template.format(CIVIC_ADDRESS_PREFIX, 'country'))
        civic.a1 = self._run_xpath(data, xpath_template.format(CIVIC_ADDRESS_PREFIX, 'A1'))
        civic.a2 = self._run_xpath(data, xpath_template.format(CIVIC_ADDRESS_PREFIX, 'A2'))
        civic.a3 = self._run_xpath(data, xpath_template.format(CIVIC_ADDRESS_PREFIX, 'A3'))
        civic.a4 = self._run_xpath(data, xpath_template.format(CIVIC_ADDRESS_PREFIX, 'A4'))
        civic.a5 = self._run_xpath(data, xpath_template.format(CIVIC_ADDRESS_PREFIX, 'A5'))
        civic.a6 = self._run_xpath(data, xpath_template.format(CIVIC_ADDRESS_PREFIX, 'A6'))
        civic.prm = self._run_xpath(data, xpath_template.format(CIVIC_ADDRESS_PREFIX, 'PRM'))
        civic.prd = self._run_xpath(data, xpath_template.format(CIVIC_ADDRESS_PREFIX, 'PRD'))
        civic.rd = self._run_xpath(data, xpath_template.format(CIVIC_ADDRESS_PREFIX, 'RD'))
        civic.sts = self._run_xpath(data, xpath_template.format(CIVIC_ADDRESS_PREFIX, 'STS'))
        civic.pod = self._run_xpath(data, xpath_template.format(CIVIC_ADDRESS_PREFIX, 'POD'))
        civic.pom = self._run_xpath(data, xpath_template.format(CIVIC_ADDRESS_PREFIX, 'POM'))
        civic.rdsec = self._run_xpath(data, xpath_template.format(CIVIC_ADDRESS_PREFIX, 'RDSEC'))
        civic.rdbr = self._run_xpath(data, xpath_template.format(CIVIC_ADDRESS_PREFIX, 'RDBR'))
        civic.rdsubr = self._run_xpath(data, xpath_template.format(CIVIC_ADDRESS_PREFIX, 'RDSUBBR'))
        civic.hno = self._run_xpath(data, xpath_template.format(CIVIC_ADDRESS_PREFIX, 'HNO'))
        civic.hns = self._run_xpath(data, xpath_template.format(CIVIC_ADDRESS_PREFIX, 'HNS'))
        civic.lmk = self._run_xpath(data, xpath_template.format(CIVIC_ADDRESS_PREFIX, 'LMK'))
        civic.loc = self._run_xpath(data, xpath_template.format(CIVIC_ADDRESS_PREFIX, 'LOC'))
        civic.flr = self._run_xpath(data, xpath_template.format(CIVIC_ADDRESS_PREFIX, 'FLR'))
        civic.nam = self._run_xpath(data, xpath_template.format(CIVIC_ADDRESS_PREFIX, 'NAM'))
        civic.pc = self._run_xpath(data, xpath_template.format(CIVIC_ADDRESS_PREFIX, 'PC'))
        civic.bld = self._run_xpath(data, xpath_template.format(CIVIC_ADDRESS_PREFIX, 'BLD'))
        civic.unit = self._run_xpath(data, xpath_template.format(CIVIC_ADDRESS_PREFIX, 'UNIT'))
        civic.room = self._run_xpath(data, xpath_template.format(CIVIC_ADDRESS_PREFIX, 'ROOM'))
        civic.seat = self._run_xpath(data, xpath_template.format(CIVIC_ADDRESS_PREFIX, 'SEAT'))
        civic.pl = self._run_xpath(data, xpath_template.format(CIVIC_ADDRESS_PREFIX, 'PLC'))
        civic.pcn = self._run_xpath(data, xpath_template.format(CIVIC_ADDRESS_PREFIX, 'PCN'))
        civic.pobox = self._run_xpath(data, xpath_template.format(CIVIC_ADDRESS_PREFIX, 'POBOX'))
        civic.addcode = self._run_xpath(data, xpath_template.format(CIVIC_ADDRESS_PREFIX, 'ADDCODE'))
        civic.stp = self._run_xpath(data, xpath_template.format(CAE_PREFIX, 'STP'))
        civic.stps = self._run_xpath(data, xpath_template.format(CAN_PREFIX, 'STPS'))
        return civic

    def format(self, data):
        """
        Formats a civic address.

        :param data: The address to be formatted.
        :type data: :py:class:`CivicAddress`
        :return: The formatted output.
        :rtype: :py:class:`_ElementTree`
        """
        raise NotImplementedError('TODO: Implement formatting of civic addresses.')


class PointXmlConverter(XmlConverter):
    """
    Implementation class for converting points from/to XML.
    """
    def __init__(self):
        """
        Constructs a new PointXmlParser instance.
        
        :return PointXmlParser: A new PointXmlParser instance.
        """
        super(PointXmlConverter, self).__init__()

    def parse(self, data):
        """
        Parse a node containing a point.
        
        :param data: The point node.
        :type data: :py:class:`_ElementTree`
        :return: A Point instance.
        :rtype: :py:class:`Point`
        """
        sr_template = './@{0}'
        point_template = './{0}:{1}/text()'
        point = Point()
        point.spatial_ref = self._run_xpath(data, sr_template.format('srsName'))
        position = self._run_xpath(data, point_template.format(GML_PREFIX, 'pos'))
        lat, lon = position.split()
        point.latitude = float(lat)
        point.longitude = float(lon)

        return point

    def format(self, data):
        """
        Formats a point.

        :param data: The point to be formatted.
        :type data: :py:class:`Point`
        :return: The formatted output.
        :rtype: :py:class:`_ElementTree`
        """
        raise NotImplementedError('TODO: Implement formatting of points.')


class CircleXmlConverter(XmlConverter):
    """
    Implementation class for converting circles from/to XML.
    """
    def __init__(self):
        """
        Constructs a new CircleXmlParser instance.
        
        :return CircleXmlParser: A new CircleXmlParser instance.
        """
        super(CircleXmlConverter, self).__init__()

    def parse(self, data):
        """
        Parse a node containing a circle.
        
        :param data: The circle node.
        :type data: :py:class:`_ElementTree`
        :return: A Circle instance.
        :rtype: :py:class:`Circle`
        """
        sr_template = './@{0}'
        node_template = './{0}:{1}/text()'
        uom_template = './{0}:{1}/@{2}'

        circle = Circle()
        circle.spatial_ref = self._run_xpath(data, sr_template.format('srsName'))

        position = self._run_xpath(data, node_template.format(GML_PREFIX, 'pos'))
        lat, lon = position.split()
        circle.latitude = float(lat)
        circle.longitude = float(lon)

        circle.radius = self._run_xpath(data, node_template.format(PIDFLO_PREFIX, 'radius'))
        circle.uom = self._run_xpath(data, uom_template.format(PIDFLO_PREFIX, 'radius', 'uom'))

        return circle

    def format(self, data):
        """
        Formats a circle.

        :param data: The circle to be formatted.
        :type data: :py:class:`Circle`
        :return: The formatted output.
        :rtype: :py:class:`_ElementTree`
        """
        raise NotImplementedError('TODO: Implement formatting of circles.')


class LocationXmlConverter(XmlConverter):
    """
    Implementation class for converting LoST location elements.
    """
    def __init__(self):
        """
        Constructs a new LocationXmlParser instance.
        """
        super(LocationXmlConverter, self).__init__()

    def _parse_geodetic(self, data):
        """
        Parses a node containing one of the geodetic-2d location types.
        
        :param data: The node containing the geometry to be parsed.
        :type data: :py:class:`_ElementTree`
        :return: A model instance representing the geometry.
        :rtype: A subclass of :py:class:`Geodetic2D` 
        """
        retval = None
        parser = None
        qname = etree.QName(data)
        if 'Point' == qname.localname:
            parser = PointXmlConverter()
        elif 'Circle':
            parser = CircleXmlConverter()
        retval = parser.parse(data)
        return retval

    def parse(self, data):
        """
        Parse a node containing a location.
        
        :param data: The location node.
        :type data: :py:class:`_ElementTree`
        :return: A Location instance.
        :rtype: :py:class:`Location`
        """
        location = Location()
        location.id = data.attrib['id']
        location.profile = data.attrib['profile']

        if 'geodetic-2d' == location.profile:
            location.location = self._parse_geodetic(data[0])
        else:
            civic_parser = CivicXmlConverter()
            location.location = civic_parser.parse(data[0])

        return location

    def format(self, data):
        """
        Formats a location.

        :param data: The location to be formatted.
        :type data: :py:class:`Location`
        :return: The formatted output.
        :rtype: :py:class:`_ElementTree`
        """
        raise NotImplementedError('TODO: Implement formatting of locations.')


class FindServiceXmlConverter(XmlConverter):
    """
    Implementation class for converting findService requests and responses.
    """

    def __init__(self):
        """
        Constructs a new FindServiceXmlParser instance.
        """
        super(FindServiceXmlConverter, self).__init__()

    def parse(self, data):
        """
        Parse a findService LoST request.
        
        :param data: The findService request XML.
        :type data: ``str`` or :py:class:`_ElementTree`
        :return: A FindServiceRequest instance.
        :rtype: :py:class:`FindServiceRequest`
        """
        root = self.get_root(data)

        request = FindServiceRequest()

        location_parser = LocationXmlConverter()

        location = root.find('{urn:ietf:params:xml:ns:lost1}location')
        request.location = location_parser.parse(location)
        request.service = root.find('{urn:ietf:params:xml:ns:lost1}service').text

        return request

    def format(self, data):
        """
        Formats a findService LoST response.

        :param data: The response to be formatted.
        :type data: :py:class:`FindServiceResponse`
        :return: The formatted output.
        :rtype: :py:class:`_ElementTree`
        """

        # create the root element of the xml response.
        xml_response = lxml.etree.Element('findServiceResponse', nsmap={None: LOST_URN})
        # Add mapping sub element
        mapping = lxml.etree.SubElement(xml_response, 'mapping', attrib={'expires': 'NO-CACHE', 'lastUpdated': '', 'source':'', 'sourceId':''})

        # add the displayname, serviceurn, routeuri, servicenum to mapping
        services_element = lxml.etree.SubElement(mapping, 'displayName')
        services_element.text = data.displayname

        services_element = lxml.etree.SubElement(mapping, 'service')
        services_element.text = data.serviceurn

        services_element = lxml.etree.SubElement(mapping, 'uri')
        services_element.text = data.routeuri

        services_element = lxml.etree.SubElement(mapping, 'serviceNumber')
        services_element.text = data.servicenum

        # TODO serviceBoundaryReference- does order matter?
        # services_element = lxml.etree.SubElement(mapping, 'serviceBoundaryReference')
        # services_element.text = data.servicenum


        # add the path element
        path_element = lxml.etree.SubElement(xml_response, 'path')

        # not generate a 'via' element for each source.
        if data.path is not None:
            for a_path in data.path:
                via_element = lxml.etree.SubElement(path_element, 'via', attrib={'source': a_path})

        # TODO locationUsed
        # services_element = lxml.etree.SubElement(xml_response, 'locationUsed')
        # services_element.text = ' '.join(data.servicenum)


        return xml_response

        # raise NotImplementedError('TODO: Implement formatting of FindServiceResponses.')


class ListServicesXmlConverter(XmlConverter):
    """
    Implementation class for converting listServices requests and responses.
    """

    def __init__(self):
        """
        Constructs a new ListServicesXmlConverter instance.
        """
        super(ListServicesXmlConverter, self).__init__()

    def parse(self, data):
        """
        Parse a listServices LoST request.

        :param data: The listServices request XML.
        :type data: ``str`` or :py:class:`_ElementTree`
        :return: A ListServicesRequest instance.
        :rtype: :py:class:`ListServicesRequest`
        """
        root = self.get_root(data)
        request = ListServicesRequest()
        try:
            request.service = root.find('{urn:ietf:params:xml:ns:lost1}service').text
        except:
            request.service = None

        return request

    def format(self, data):
        """
        Formats a listServices LoST response.

        :param data: The response to be formatted.
        :type data: :py:class:`ListServicesResponse`
        :return: The formatted output.
        :rtype: :py:class:`_ElementTree`
        """
        # create the root element of the xml response.
        xml_response = lxml.etree.Element('listServicesResponse', nsmap={None: LOST_URN})
        # add the services element, filling in with the list of services in the reponse.
        services_element = lxml.etree.SubElement(xml_response, 'serviceList')
        services_element.text = ' '.join(data.services)
        # add the path element 
        path_element = lxml.etree.SubElement(xml_response, 'path')
        # not generate a 'via' element for each source.
        if data.path is not None:
            for a_path in data.path:
                via_element = lxml.etree.SubElement(path_element, 'via', attrib={'source': a_path})
        
        return xml_response


class ListServicesByLocationXmlConverter(XmlConverter):
    """
    Implementation class for converting listServicesByLocation requests and responses.
    """

    def __init__(self):
        """
        Constructs a new ListServicesByLocationXmlConverter instance.
        """
        super(ListServicesByLocationXmlConverter, self).__init__()

    def parse(self, data):
        """
        Parse a listServicesByLocation LoST request.

        :param data: The listServicesByLocation request XML.
        :type data: ``str`` or :py:class:`_ElementTree`
        :return: A ListServicesByLocationRequest instance.
        :rtype: :py:class:`ListServicesByLocationRequest`
        """
        raise NotImplementedError("Can't parse listServicesByLocation requests just yet, come back later.")

    def format(self, data):
        """
        Formats a listServicesByLocation LoST response.

        :param data: The response to be formatted.
        :type data: :py:class:`ListServicesByLocationResponse`
        :return: The formatted output.
        :rtype: :py:class:`_ElementTree`
        """
        raise NotImplementedError('TODO: Implement formatting of ListServicesByLocationResponses.')


class GetServiceBoundaryXmlConverter(XmlConverter):
    """
    Implementation class for converting getServiceBoundary requests and responses.
    """

    def __init__(self):
        """
        Constructs a new GetServiceBoundaryXmlConverter instance.
        """
        super(GetServiceBoundaryXmlConverter, self).__init__()

    def parse(self, data):
        """
        Parse a getServiceBoundary LoST request.

        :param data: The getServiceBoundary request XML.
        :type data: ``str`` or :py:class:`_ElementTree`
        :return: A GetServiceBoundaryRequest instance.
        :rtype: :py:class:`GetServiceBoundaryRequest`
        """
        raise NotImplementedError("Can't parse getServiceBoundary requests just yet, come back later.")

    def format(self, data):
        """
        Formats a getServiceBoundary LoST response.

        :param data: The response to be formatted.
        :type data: :py:class:`GetServiceBoundaryResponse`
        :return: The formatted output.
        :rtype: :py:class:`_ElementTree`
        """
        raise NotImplementedError('TODO: Implement formatting of GetServiceBoundaryResponses.')





