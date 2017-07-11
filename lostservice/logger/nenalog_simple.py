#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. currentmodule:: lostservice.logger.nenalog
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

Auditing framework.
"""

import datetime
import uuid
from lostservice.converting.xml import FindServiceXmlConverter
from lostservice.model.location import Circle
from lostservice.model.location import Location

from zeep import Client
from zeep import xsd
from zeep import helpers
from lxml import etree


class NENALoggingException(Exception):
    """
    Raised when something goes wrong in the process of logging.

    :param message: The exception message
    :type message:  ``str``
    :param nested: Nested exception, if any.
    :type nested:
    """
    def __init__(self, message, nested=None):
        super().__init__(message)
        self._nested = nested


def create_NENA_log_events(request_text, query_type, start_time, response_text, end_time, server_id):
    # add query_ip_port, response_ip_port

    # Create Log ID used for both Request and Response
    nena_log_id = uuid.uuid4()

    # client = Client('http://localhost:52759/Logging.asmx?wsdl')
    client = Client('http://LP-DSTOICK-1:8088/mockLoggingBinding?wsdl', strict=False)

    # Create LoSTQueryBodyType Item

    # Create DirectionValuesCode of "incoming"
    direction_values_code_type = client.get_type('ns6:DirectionValuesCodeType')
    direction_values_code_simple_type = client.get_type('ns6:DirectionValuesCodeSimpleType')
    direction_values_code_simple = direction_values_code_simple_type('incoming')
    direction_values_code = direction_values_code_type(direction_values_code_simple)

    body_type = client.get_type('ns2:LoSTQueryBodyType')
    lost_query_adapter_type = client.get_type('ns2:LoSTQueryAdapterType')

    # Create FindService
    find_service_element = client.get_element('ns10:findService')
    location_element = client.get_element('ns10:location')

    # loc = {'Circle': {'spatial_ref': 'urn:ogc:def:crs:EPSG::4326', 'lon': -68.4977255651657,
    #                   'radius': '916105.41237061098', 'uom': 'urn:ogc:def:uom:EPSG::9001',
    #                   'lat': 45.4430670070877}}

    loc = """<gs:Circle xmlns:gs="http://www.opengis.net/pidflo/1.0" xmlns:gml="http://www.opengis.net/gml" srsName="urn:ogc:def:crs:EPSG::4326">
                <gml:pos>45.4430670070877 -68.4977255651657</gml:pos>
                <gs:radius uom="urn:ogc:def:uom:EPSG::9001">916105.41237061098</gs:radius>
            </gs:Circle>"""

    id = '24b276e1-7eca-48d5-be24-30e0dd4c1ca0'
    profile = 'geodetic-2d'

    service = {'service': 'urn:nena:service:sos.police'}
    #serb = {'serviceBoundary': 'reference'}

    # Get location as array?
    location = location_element()

    location['_value_1'] = loc
    location['profile'] = profile
    location['id'] = id

    # service = client.get_element('ns10:service')
    path_element = client.get_element('ns10:path')
    via_element = client.get_element('ns10:via')
    serviceBoundary_element = client.get_element('ns10:serviceBoundary')
    uri_element = client.get_element('ns10:uri')

    via = via_element()
    path = path_element(via)
    uri = uri_element('test')
    service_boundary = serviceBoundary_element()

    # find_service = find_service_element(location=[location_array], service=ser, path=path, validateLocation=True,
    #                                    serviceBoundary=service_boundary, recursive=False)

    # find_service = find_service_element([location], service, path, True, service_boundary, False)
    find_service = find_service_element([location], service, path, uri, True, service_boundary, False)

    # use fine_service to create lost_query_adapter
    obj = lost_query_adapter_type(findService=find_service)

    body = body_type(LoSTQueryId=str(nena_log_id), DirectionValuesCode=direction_values_code,
                     LoSTQueryAdapter=obj)

    # Create EventValuesCode of "LoSTQuery"
    event_values_code_type = client.get_type('ns6:EventValuesCodeType')
    event_values_code_simple_type = client.get_type('ns6:EventValuesCodeSimpleType')
    event_values_code_simple = event_values_code_simple_type('LoSTQuery')
    event_values_code = event_values_code_type(event_values_code_simple)

    result = client.service.LogEvent(LogEventTimestamp=start_time, ElementId=server_id,
                                     EventValuesCode=event_values_code,
                                     OtherElementAddress='string', LogEventBody=body, AgencyId=1)

    print(result)
