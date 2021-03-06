#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: lostservice.converting.xml
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

Xml conversion classes.
"""

import collections
import io

import lxml
import numpy
from lxml import etree

from lostservice.converter import Converter
from lostservice.exception import LocationProfileException, BadRequestException
from lostservice.exception import NotFoundException
from lostservice.model.civic import CivicAddress
from lostservice.model.geodetic import Arcband
from lostservice.model.geodetic import Circle
from lostservice.model.geodetic import Ellipse
from lostservice.model.geodetic import Point
from lostservice.model.geodetic import Polygon
from lostservice.model.location import Location
from lostservice.model.requests import FindServiceRequest
from lostservice.model.requests import GetServiceBoundaryRequest
from lostservice.model.requests import ListServicesByLocationRequest
from lostservice.model.requests import ListServicesRequest
from lostservice.model.responses import AdditionalDataResponseMapping, ResponseMapping

from lostservice.configuration import general_logger
logger = general_logger()


LOST_PREFIX = 'lost'
LOST_URN = 'urn:ietf:params:xml:ns:lost1'
CIVIC_ADDRESS_PREFIX = 'civ'
CIVIC_ADDRESS_URN = 'urn:ietf:params:xml:ns:pidf:geopriv10:civicAddr'
PIDFLO_PREFIX = 'gs'
PIDFLO_URN = 'http://www.opengis.net/pidflo/1.0'
GML_PREFIX = 'gml'
GML_URN = 'http://www.opengis.net/gml'
GML_URN_COORDS = '{0}{1}{2}'.format('{',GML_URN,'}')
CAN_PREFIX = 'can'
CAN_URN = 'urn:nena:xml:ns:pidf:nenaCivicAddr'
CAE_PREFIX = 'cae'
CAE_URN = 'urn:ietf:params:xml:ns:pidf:geopriv10:civicAddr:ext'
GEO_PROFILE = 'geodetic-2d'

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
            logger.warning('Invalid xpath request.')
            raise BadRequestException('Invalid xpath request.')

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
        civic.stp = self._run_xpath(data, xpath_template.format(CIVIC_ADDRESS_PREFIX, 'STP'))
        civic.stps = self._run_xpath(data, xpath_template.format(CIVIC_ADDRESS_PREFIX, 'STPS'))
        civic.hnp = self._run_xpath(data, xpath_template.format(CIVIC_ADDRESS_PREFIX, 'HNP'))
        civic.lmkp = self._run_xpath(data, xpath_template.format(CIVIC_ADDRESS_PREFIX, 'LMKP'))
        civic.mp = self._run_xpath(data, xpath_template.format(CIVIC_ADDRESS_PREFIX, 'MP'))
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
        try:
            point.spatial_ref = self._run_xpath(data, sr_template.format('srsName'))
            position = self._run_xpath(data, point_template.format(GML_PREFIX, 'pos'))
            lat, lon = position.split()
            point.latitude = float(lat)
            point.longitude = float(lon)
        except (Exception, TypeError) as ex:
            logger.error('Invalid point input.', ex)
            raise BadRequestException('Invalid point input.')

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
        try:
            circle.spatial_ref = self._run_xpath(data, sr_template.format('srsName'))

            position = self._run_xpath(data, node_template.format(GML_PREFIX, 'pos'))
            lat, lon = position.split()
            circle.latitude = float(lat)
            circle.longitude = float(lon)

            circle.radius = float(self._run_xpath(data, node_template.format(PIDFLO_PREFIX, 'radius')))
            circle.uom = self._run_xpath(data, uom_template.format(PIDFLO_PREFIX, 'radius', 'uom'))
        except (Exception, TypeError) as ex:
            logger.error('Invalid circle input.', ex)
            raise BadRequestException('Invalid circle input.')

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


class PolygonXmlConverter(XmlConverter):
    """
    Implementation class for converting polygon points from/to XML.
    """

    def __init__(self):
        """
        Constructs a new PolygonXmlConverter instance.

        :return PointXmlParser: A new PolygonXmlConverter instance.
        """
        super(PolygonXmlConverter, self).__init__()

    def parse(self, data):
        """
        Parse a node containing a polygon.

        :param data: The polygon node.
        :type data: :py:class:`_ElementTree`
        :return: A Polygon instance.
        :rtype: :py:class:`Polygon`
        """
        model = Polygon()
        try:
            sr_template = './@{0}'
            # point_template = './{0}:{1}/text()'

            model.spatial_ref = self._run_xpath(data, sr_template.format('srsName'))
            for polygon in data.findall('{0}exterior'.format(GML_URN_COORDS)):
                for coord in polygon.findall("{0}LinearRing/".format(GML_URN_COORDS)):
                    position = coord.text
                    if coord.tag == "{0}posList".format(GML_URN_COORDS):
                        # format of GML is gml:posList
                        sublist = numpy.array_split(position.split(), (len(position.split())) / 2)
                        for item in sublist:
                            lat = item[0]
                            lon = item[1]
                            point = [float(lon), float(lat)]
                            model.vertices.append(point)
                    else:
                        # format of GML is gml:pos
                        lat, lon = position.split()
                        point = [float(lon), float(lat)]
                        model.vertices.append(point)

        except (Exception, IndexError, TypeError) as ex:
            logger.error('Invalid polygon input.', ex)
            raise BadRequestException('Invalid polygon input.')

        if not model.vertices:
            logger.error('Invalid polygon input.')
            raise BadRequestException('Invalid polygon input.')

        return model

    def format(self, data):
        """
        Formats a point.

        :param data: The point to be formatted.
        :type data: :py:class:`Point`
        :return: The formatted output.
        :rtype: :py:class:`_ElementTree`
        """
        raise NotImplementedError('TODO: Implement formatting of points.')


class EllipseXmlConverter(XmlConverter):
    """
    Implementation class for converting ellipse points from/to XML.
    """

    def __init__(self):
        """
        Constructs a new EllipseXmlConverter instance.

        :return: A new EllipseXmlConverter instance.
        """
        super(EllipseXmlConverter, self).__init__()

    def parse(self, data):
        """
        Parse a node containing an ellipse.

        :param data: The ellipse node.
        :type data: :py:class:`_ElementTree`
        :return: A Ellipse instance.
        :rtype: :py:class:`Ellipse`
        """
        sr_template = './@{0}'
        node_template = './{0}:{1}/text()'
        uom_template = './{0}:{1}/@{2}'

        ellipse = Ellipse()
        try:
            ellipse.spatial_ref = self._run_xpath(data, sr_template.format('srsName'))

            position = self._run_xpath(data, node_template.format(GML_PREFIX, 'pos'))
            lat, lon = position.split()
            ellipse.latitude = float(lat)
            ellipse.longitude = float(lon)

            ellipse.majorAxis = float(self._run_xpath(data, node_template.format(PIDFLO_PREFIX, 'semiMajorAxis')))
            ellipse.minorAxis = float(self._run_xpath(data, node_template.format(PIDFLO_PREFIX, 'semiMinorAxis')))
            ellipse.orientation = \
                float(0.0174532925) * float(self._run_xpath(data, node_template.format(PIDFLO_PREFIX, 'orientation')))
            ellipse.majorAxisuom = self._run_xpath(data, uom_template.format(PIDFLO_PREFIX, 'semiMajorAxis', 'uom'))
            ellipse.minorAxisuom = self._run_xpath(data, uom_template.format(PIDFLO_PREFIX, 'semiMinorAxis', 'uom'))
            ellipse.orientationuom = self._run_xpath(data, uom_template.format(PIDFLO_PREFIX, 'orientation', 'uom'))
        except (Exception, TypeError) as ex:
            logger.error('Invalid ellipse input.', ex)
            raise BadRequestException('Invalid ellipse input.')

        return ellipse

    def format(self, data):
        """
        Formats an ellipse.

        :param data: The ellipse to be formatted.
        :type data: :py:class:`Ellipse`
        :return: The formatted output.
        :rtype: :py:class:`_ElementTree`
        """
        raise NotImplementedError('TODO: Implement formatting of ellipses.')


class ArcbandXmlConverter(XmlConverter):
    """
    Implementation class for converting Arcband elements.
    """
    def __init__(self):
        super(ArcbandXmlConverter, self).__init__()

    def parse(self, data):
        """
        Parse a node containing an arcband.

        :param data: The arcband node.
        :type data: :py:class:`_ElementTree`
        :return: An Arcband instance.
        :rtype: :py:class:`Arcband`
        """
        sr_template = './@{0}'
        node_template = './{0}:{1}/text()'
        uom_template = './{0}:{1}/@{2}'

        arcband = Arcband()
        try:
            arcband.spatial_ref = self._run_xpath(data, sr_template.format('srsName'))

            position = self._run_xpath(data, node_template.format(GML_PREFIX, 'pos'))
            lat, lon = position.split()
            arcband.latitude = float(lat)
            arcband.longitude = float(lon)

            arcband.inner_radius = float(self._run_xpath(data, node_template.format(PIDFLO_PREFIX, 'innerRadius')))
            arcband.inner_radius_uom = self._run_xpath(data, uom_template.format(PIDFLO_PREFIX, 'innerRadius', 'uom'))
            arcband.outer_radius = float(self._run_xpath(data, node_template.format(PIDFLO_PREFIX, 'outerRadius')))
            arcband.outer_radius_uom = self._run_xpath(data, uom_template.format(PIDFLO_PREFIX, 'outerRadius', 'uom'))
            arcband.start_angle = float(self._run_xpath(data, node_template.format(PIDFLO_PREFIX, 'startAngle')))
            arcband.start_angle_uom = self._run_xpath(data, uom_template.format(PIDFLO_PREFIX, 'startAngle', 'uom'))
            arcband.opening_angle = float(self._run_xpath(data, node_template.format(PIDFLO_PREFIX, 'openingAngle')))
            arcband.opening_angle_uom = self._run_xpath(data, uom_template.format(PIDFLO_PREFIX, 'openingAngle', 'uom'))
        except (Exception, TypeError) as ex:
            logger.error('Invalid arcband input.', ex)
            raise BadRequestException('Invalid arcband input.')

        return arcband

    def format(self, data):
        """
        Formats an arcband.

        :param data: The arcband to be formatted.
        :type data: :py:class:`Arcband`
        :return: The formatted output.
        :rtype: :py:class:`_ElementTree`
        """
        raise NotImplementedError('TODO: Implement formatting of arcbands.')


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
        elif 'Polygon' == qname.localname:
            parser = PolygonXmlConverter()
        elif 'Ellipse' == qname.localname:
            parser = EllipseXmlConverter()
        elif 'Circle' == qname.localname:
            parser = CircleXmlConverter()
        elif 'ArcBand' == qname.localname:
            parser = ArcbandXmlConverter()
        else:
            logger.warning('Invalid geometry: {0}'.format(qname))
            raise BadRequestException('Invalid geometry: {0}'.format(qname))

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
        try:
            location.id = data.attrib['id']
            location.profile = data.attrib['profile']
        except Exception as ex:
            logger.error(ex)
            raise BadRequestException('Invalid location input.', ex)

        if 'geodetic-2d' == location.profile:
            location.location = self._parse_geodetic(data[0])
        elif 'civic' == location.profile:
            civic_parser = CivicXmlConverter()
            location.location = civic_parser.parse(data[0])
        else:
            logger.warning('{0} is not a valid location profile.'.format(location.profile), None)
            raise LocationProfileException('{0} is not a valid location profile.'.format(location.profile), None)

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


class PathXmlConverter(XmlConverter):
    """
    Implementation class for converting LoST path elements.
    """
    def __init__(self):
        """
        Constructs a new PathXmlParser instance.
        """
        super(PathXmlConverter, self).__init__()

    def parse(self, data):
        """
        Parse a node containing a path.

        :param data: The path node.
        :type data: :py:class:`_ElementTree`
        :return: A Path instance.
        :rtype: list of object `source`
        """

        source_list = []

        for item in data:
            source = item.attrib['source']
            source_list.append(source)

        return source_list


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

        try:
            if 'serviceBoundary' in root.attrib:
                request.serviceBoundary = root.attrib['serviceBoundary']

            if 'validateLocation' in root.attrib:
                request.validateLocation = root.attrib['validateLocation']

            for element in root.iter():
                if element.tag == '{urn:ietf:params:xml:ns:lost1}location':
                    location_parser = LocationXmlConverter()
                    request.location = location_parser.parse(element)

                elif element.tag == '{urn:ietf:params:xml:ns:lost1}service':
                    request.service = element.text.strip()

                elif element.tag == '{urn:ietf:params:xml:ns:lost1}path':
                    path_parser = PathXmlConverter()
                    request.path = path_parser.parse(element)
                else:
                    if (LOST_URN not in element.tag) and (
                                PIDFLO_URN not in element.tag) and (
                                GML_URN not in element.tag) and (
                            CIVIC_ADDRESS_URN not in element.tag):
                        request.nonlostdata.append(element)
        except (BadRequestException, LocationProfileException) as ex:
            logger.error(ex)
            raise
        except Exception as ex:
            logger.error('Invalid request.', ex)
            raise BadRequestException('Invalid request.')

        return request

    def format(self, data):
        """
        Formats a findService LoST response.

        :param data: The response to be formatted.
        :type data: :py:class:`FindServiceResponse`
        :return: The formatted output.
        :rtype: :py:class:`_ElementTree`
        """
        if data.mappings is None or len(data.mappings) == 0:
            logger.warning('Could not find an answer to the request.', None)
            raise NotFoundException('Could not find an answer to the request.', None)

        # create the root element of the xml response.
        xml_response = lxml.etree.Element('findServiceResponse', nsmap={None: LOST_URN, GML_PREFIX: GML_URN})
        for item in data.mappings:
            # Add mapping sub element
            mapping = lxml.etree.SubElement(xml_response,
                                            'mapping',
                                            attrib={'expires': item.expires,
                                                    'lastUpdated': str(item.last_updated),
                                                    'source': item.source,
                                                    'sourceId': item.source_id})

            # add the displayname, serviceurn, routeuri, servicenum to mapping
            services_element = lxml.etree.SubElement(mapping, 'service')
            services_element.text = item.service_urn
            if type(item) is ResponseMapping:
                services_element = lxml.etree.SubElement(mapping, 'displayName')
                services_element.text = item.display_name

                attr = services_element.attrib
                attr['{http://www.w3.org/XML/1998/namespace}lang'] = 'en'

                services_element = lxml.etree.SubElement(mapping, 'uri')
                services_element.text = item.route_uri

                services_element = lxml.etree.SubElement(mapping, 'serviceNumber')
                services_element.text = item.service_number

                # if boundary_value = None do not add serviceBoundary tag to the response (override setting)
                # if boundary_value = "" then include serviceBoundaryReference tag
                # if boundary_value contains value then include serviceBoundary tag
                if item.boundary_value is not None:
                    if item.boundary_value == "":
                        attr_element = collections.OrderedDict()
                        attr_element['source'] = item.source
                        attr_element['key'] = item.source_id
                        lxml.etree.SubElement(mapping, 'serviceBoundaryReference', attrib=attr_element)
                    else:
                        # TODO - fix the profile.
                        services_element = lxml.etree.SubElement(mapping, 'serviceBoundary', profile='geodetic-2d')

                        final_gml_as_xml = io.StringIO('''<root xmlns:gml="{0}">{1}</root>'''.format(GML_URN, item.boundary_value))
                        final_gml = etree.parse(final_gml_as_xml).getroot()
                        services_element.extend(final_gml)

            elif type(item) is AdditionalDataResponseMapping:
                services_element = lxml.etree.SubElement(mapping, 'uri')
                services_element.text = item.adddatauri

            if hasattr(item,"locationValidation"):
                # add the validation element
                validation_element = lxml.etree.SubElement(xml_response, 'locationValidation')
                if item.locationValidation.get("valid"):
                    valid_element = lxml.etree.SubElement(validation_element, 'valid')
                    valid_element.text = item.locationValidation.get("valid")
                if item.locationValidation.get("invalid"):
                    invalid_element = lxml.etree.SubElement(validation_element, 'invalid')
                    invalid_element.text = item.locationValidation.get("invalid")
                if item.locationValidation.get("unchecked"):
                    unchecked_element = lxml.etree.SubElement(validation_element,'unchecked')
                    unchecked_element.text = item.locationValidation.get("unchecked")


        # add the path element
        path_element = lxml.etree.SubElement(xml_response, 'path')

        # not generate a 'via' element for each source.
        if data.path is not None:
            for a_path in data.path:
                via_element = lxml.etree.SubElement(path_element, 'via', attrib={'source': a_path})

        lxml.etree.SubElement(
            xml_response,
            'locationUsed',
            attrib={'id': data.location_used}
        )

        # Add NonLoSTdata items into response (pass though items)
        for nonlost_item in data.nonlostdata:
            xml_response.append(nonlost_item)

        return xml_response


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

        for element in root.iter():
            if element.tag == '{urn:ietf:params:xml:ns:lost1}service':
                request.service = element.text

            elif element.tag == '{urn:ietf:params:xml:ns:lost1}path':
                path_parser = PathXmlConverter()
                request.path = path_parser.parse(element)

            else:
                if (LOST_URN not in element.tag) and (
                            PIDFLO_URN not in element.tag) and (
                            GML_URN not in element.tag):
                    request.nonlostdata.append(element)

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

        # Add NonLoSTdata items into response (pass though items)
        for nonlost_item in data.nonlostdata:
            xml_response.append(nonlost_item)

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

        root = self.get_root(data)
        request = ListServicesByLocationRequest()

        for element in root.iter():
            if element.tag == '{urn:ietf:params:xml:ns:lost1}location':
                location_parser = LocationXmlConverter()
                request.location = location_parser.parse(element)
            if element.tag == '{urn:ietf:params:xml:ns:lost1}service':
                request.service = element.text
            elif element.tag == '{urn:ietf:params:xml:ns:lost1}path':
                path_parser = PathXmlConverter()
                request.path = path_parser.parse(element)
            elif element.tag == '{urn:ietf:params:xml:ns:lost1}location':
                request.location_id = element.attrib.get('id')
            else:
                if (LOST_URN not in element.tag) and (
                            PIDFLO_URN not in element.tag) and (
                            GML_URN not in element.tag and
                            CIVIC_ADDRESS_URN not in element.tag):
                    request.nonlostdata.append(element)
        return request

    def format(self, data):
        """
        Formats a listServicesByLocation LoST response.

        :param data: The response to be formatted.
        :type data: :py:class:`ListServicesByLocationResponse`
        :return: The formatted output.
        :rtype: :py:class:`_ElementTree`
        """
        # create the root element of the xml response.
        xml_response = lxml.etree.Element('listServicesByLocationResponse', nsmap={None: LOST_URN})
        # add the services element, filling in with the list of services in the response.
        services_element = lxml.etree.SubElement(xml_response, 'serviceList')
        if data.services:
            services_element.text = ' '.join(data.services)

        # add the path element
        path_element = lxml.etree.SubElement(xml_response, 'path')

        # services_element = lxml.etree.SubElement(xml_response, 'locationUsed')
        # services_element.text = data.location_id

        # not generate a 'via' element for each source.
        if data.path is not None:
            for a_path in data.path:
                via_element = lxml.etree.SubElement(path_element, 'via', attrib={'source': a_path})

        lxml.etree.SubElement(xml_response, 'locationUsed', attrib={'id': data.location_id})
        # Add NonLoSTdata items into response (pass though items)
        for nonlost_item in data.nonlostdata:
            xml_response.append(nonlost_item)

        return xml_response


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
        root = self.get_root(data)
        request = GetServiceBoundaryRequest()
        try:
            request.key = root.get("key")
        except:
            logger.error('Request key not found!')
            request.key = None

        for element in root.iter():
            if (LOST_URN not in element.tag) and (
                        PIDFLO_URN not in element.tag) and (
                        GML_URN not in element.tag):
                request.nonlostdata.append(element)

        return request
        #raise NotImplementedError("Can't parse getServiceBoundary requests just yet, come back later.")

    def format(self, data):
        """
        Formats a getServiceBoundary LoST response.

        :param data: The response to be formatted.
        :type data: :py:class:`GetServiceBoundaryResponse`
        :return: The formatted output.
        :rtype: :py:class:`_ElementTree`
        """
        # create the root element of the xml response.
        xml_response = lxml.etree.Element('getServiceBoundaryResponse',
                                          nsmap={None: LOST_URN, GML_PREFIX: GML_URN})

        for item in data:
            services_element = lxml.etree.SubElement(xml_response, 'serviceBoundary', profile=item.get('profile',GEO_PROFILE))
            final_gml_as_xml = io.StringIO('''<root xmlns:gml="{0}">{1}</root>'''.format(GML_URN, item['ST_AsGML_1']))
            final_gml = etree.parse(final_gml_as_xml).getroot()
            services_element.extend(final_gml)

        if data[0] is not None:
            # add the path element
            path_element = lxml.etree.SubElement(xml_response, 'path')
            # not generate a 'via' element for each source.
            if data[0]['path'] is not None:
                via_element = lxml.etree.SubElement(path_element, 'via', attrib={'source': data[0]['path']})

            # Add NonLoSTdata items into response (pass though items)
            for nonlost_item in data[0]['nonlostdata']:
                 xml_response.append(nonlost_item)

        return xml_response



