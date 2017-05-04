#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lxml import etree

from lostservice.converter import Converter
from lostservice.model.location import CivicAddress
from lostservice.model.location import Circle
from lostservice.model.location import Point
from lostservice.model.location import Location
from lostservice.model.requests import FindServiceRequest

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
    Implementation class for parsing civic addresses from XML.
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
    Implementation class for parsing points from XML.
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
    Implementation class for parsing circles from XML.
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
    Implementation class for parsing LoST location elements.
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
        if 'Point' == data.tag:
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
            location.geodetic2d = self._parse_geodetic(data[0])
        else:
            civic_parser = CivicXmlConverter()
            location.civic_address = civic_parser.parse(data[0])

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
    Implementation class for parsing findService requests.
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
        root = None
        try:
            doc = etree.fromstring(data)
            root = doc.getroot()
        except:
            root = data

        request = FindServiceRequest()

        location_parser = LocationXmlConverter()

        location = root.find('{urn:ietf:params:xml:ns:lost1}location')
        request.location = location_parser.parse(location)
        request.service = root.find('{urn:ietf:params:xml:ns:lost1}service').text

        return request





