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


def _send_nenalog_request(nena_log_id, request_text, query_type, start_time, server_id):

    # TODO enable cache for wsdl?
    # client = Client('http://localhost:52759/Logging.asmx?wsdl')
    client = Client('http://LP-DSTOICK-1:8088/mockLoggingBinding?wsdl', strict=False)

    # client = Client('http://LP-DSTOICK-1:8088/mockLoggingBinding?wsdl')


    # ??Only send LogEvents to a NENA logging service if the request was a HTTP POST request.

    # VB
    # NENALogEcrfQuery(requestText, queryType, startTime, nenaLogId, queryIpAndPort)
    #NENALogEcrfResponse(responseText, endTime, nenaLogId, responseIpAndPort)

    # nenaLogId - New GUID
    # queryIpAndPort Calculated
    #responseIpAndPort Calculated
    # QueryType calculated


    # "ResponseIpAndPort"
    # "EcrfResponse"

    # LogEventTimestamp - DateTime timestamp
    # ElementId -> Server ID - lost.pv-qps-2.test
    # EventValuesCode -> EventValuesCodeType -> set to EventValuesCodeSimpleType.LoSTQuery (hardcoded to this type)
    # OtherElementAddress -> IP and Port info - formate-> IP:PORT
    # LogEventBody ->

    # Not Used
    # AgencyId, AgencyAgentId, CallIdURN, IncidentIdURN, SIPCallId

    # Create LoSTQueryBodyType Item
    body =_create_lost_query_body_type_item(client, nena_log_id, request_text, query_type)



    # Create EventValuesCode of "LoSTQuery"
    event_values_code_type = client.get_type('ns6:EventValuesCodeType')
    event_values_code_simple_type = client.get_type('ns6:EventValuesCodeSimpleType')
    event_values_code_simple = event_values_code_simple_type('LoSTQuery')
    event_values_code = event_values_code_type(event_values_code_simple)


    result = client.service.LogEvent(LogEventTimestamp=start_time, ElementId=server_id,EventValuesCode=event_values_code,
                                     OtherElementAddress='string', LogEventBody=body, AgencyId=1)

    print(result)


def _create_lost_query_body_type_item(client, nena_log_id, request_text, query_type):

    # Create DirectionValuesCode of "incoming"
    direction_values_code_type = client.get_type('ns6:DirectionValuesCodeType')
    direction_values_code_simple_type = client.get_type('ns6:DirectionValuesCodeSimpleType')
    direction_values_code_simple = direction_values_code_simple_type('incoming')
    direction_values_code = direction_values_code_type(direction_values_code_simple)

    # Create Item (LoSTMalformedQuery (string) or LoSTQueryAdapter (LoSTQueryAdapterType)

    if (str.upper(query_type) != 'FINDSERVICE') and (str.upper(query_type) != 'LISTSERVICES') and (str.upper(query_type) != 'LISTSERVICESBYLOCATION') and (str.upper(query_type) != 'GETSERVICEBOUNDARY') and (str.upper(query_type) != 'MALFORMED'):
        # We don't know what type of request this was
         print('test')
    else:
        if str.upper(query_type) == 'MALFORMED':
            body_type = client.get_type('ns2:LoSTQueryBodyType')
            body = body_type(LoSTQueryId=str(nena_log_id), DirectionValuesCode=direction_values_code,
                             LoSTMalformedQuery=request_text)

        else:

            xml_request = etree.fromstring(request_text)
            findservice = FindServiceXmlConverter()
            parsed_request = findservice.parse(xml_request)

            dict_request = parsed_request.__dict__
            dict_test=_create_dictionary(dict_request)

            #find_service_element = client.get_element('ns10:findService')
            #find_service = find_service_element()

            # test1 = {'id':parsed_request.location.id, '_value_1':parsed_request.location.location, 'profile':parsed_request.location.profile}
            # test1 = {'id': parsed_request.location.id, 'profile': parsed_request.location.profile}

            # test = {'location':test1, 'service':parsed_request.service, 'serviceBoundary':parsed_request.serviceBoundary}
            # test = {'service': parsed_request.service, 'serviceBoundary': parsed_request.serviceBoundary}


            # VB Def of Nena Logging FindService
            # private location[] locationField;
            # private string serviceField;
            # private via[] pathField;
            # private System.Xml.XmlElement anyField;
            # private bool validateLocationField;
            # private bool validateLocationFieldSpecified;
            # private findServiceServiceBoundary serviceBoundaryField;
            # private bool serviceBoundaryFieldSpecified;
            # private bool recursiveField;
            # private bool recursiveFieldSpecified;

            body_type = client.get_type('ns2:LoSTQueryBodyType')


            lost_query_adapter_type = client.get_type('ns2:LoSTQueryAdapterType')

            find_service = _create_findservice(client, dict_test)





            # obj = lost_query_adapter_type(findService=find_service)

            #find_service_element = client.get_element('ns10:findService')
            # find_service = find_service_element(dict_test, xsd.SkipValue, xsd.SkipValue, xsd.SkipValue, True, xsd.SkipValue, False)
            # find_service = find_service_element(dict_test['location'], dict_test['service'], xsd.SkipValue, dict_test['serviceBoundary'], True,
            #                                    xsd.SkipValue, False)
            # Fail - find_service = find_service_element(location=dict_test)
            # find_service = find_service_element(dict_test)

            #find_service = find_service_element(dict_test['location'], dict_test['service'])

            obj = lost_query_adapter_type(findService=find_service)


            #body_type(LoSTQueryId=str(nena_log_id), DirectionValuesCode=direction_values_code,
            #                  LoSTQueryAdapter=obj)

            body = body_type(LoSTQueryId=str(nena_log_id), DirectionValuesCode=direction_values_code,
                             LoSTQueryAdapter=obj)



    return body

def _create_findservice(client, dict_test):
    find_service_element = client.get_element('ns10:findService')
    location_element = client.get_element('ns10:location')

    input_find_service = helpers.serialize_object(find_service_element)
    #input_location = helpers.serialize_object(location_element)

    t1 = input_find_service()
    #test_location = input_location()

    # location: {urn: ietf:params: xml:ns: lost1}location[],
    # service: xsd:anyURI,
    # path: {
    #     urn: ietf:params: xml:ns: lost1}path,
    # _value_1: ANY,
    # validateLocation: xsd:boolean,
    # serviceBoundary: {
    #     urn: ietf:params: xml:ns: lost1}serviceBoundary,
    # recursive: xsd:boolean



    loc = {'location': {'id': '24b276e1-7eca-48d5-be24-30e0dd4c1ca0', 'profile': 'geodetic-2d',
                  '_value_1': {'spatial_ref': 'urn:ogc:def:crs:EPSG::4326', 'lon': -68.4977255651657,
                               'radius': '916105.41237061098', 'uom': 'urn:ogc:def:uom:EPSG::9001',
                               'lat': 45.4430670070877}}}

    # loc = {'Circle': {'spatial_ref': 'urn:ogc:def:crs:EPSG::4326', 'lon': -68.4977255651657,
    #                                  'radius': '916105.41237061098', 'uom': 'urn:ogc:def:uom:EPSG::9001',
    #                                  'lat': 45.4430670070877}}
    id = '24b276e1-7eca-48d5-be24-30e0dd4c1ca0'
    profile = 'geodetic-2d'

    ser = {'service': 'urn:nena:service:sos.police'}
    serb = {'serviceBoundary': 'reference'}




    # Get location as array?
    location_array = location_element()
    # print(location_array)

    # location_array['location'] = loc
    location_array['_value_1'] = loc
    location_array['profile'] = profile
    location_array['id'] = id




    service = client.get_element('ns10:service')
    path_element = client.get_element('ns10:path')
    via_element = client.get_element('ns10:via')
    serviceBoundary_element = client.get_element('ns10:serviceBoundary')
    uri_element = client.get_element('ns10:uri')



    via = via_element()
    path = path_element(via)
    uri = uri_element('test')
    service_boundary = serviceBoundary_element()


    # LocationInformation
    location_information_type = client.get_type('ns10:locationInformation')
    location_information = location_information_type(profile=profile)

    # location = location_element(loc, profile, id)


    # Fail - Errors with 'str' object has not attribute 'keys'
    # obj = location_element(_value_1={'location': location, 'profile': profile, 'id': id})

    #Test Any object

    # lc = xsd.AnyObject(location_element, location_element({'id': '24b276e1-7eca-48d5-be24-30e0dd4c1ca0'}, {'profile': 'geodetic-2d'},{'_value_1': {'spatial_ref': 'urn:ogc:def:crs:EPSG::4326', 'lon': -68.4977255651657,
    #                            'radius': '916105.41237061098', 'uom': 'urn:ogc:def:uom:EPSG::9001',
    #                            'lat': 45.4430670070877}}))
    #
    # lc = xsd.AnyObject(location_element, location_element(id={'24b276e1-7eca-48d5-be24-30e0dd4c1ca0'},profile={'geodetic-2d'},_value_1={'spatial_ref': 'urn:ogc:def:crs:EPSG::4326', 'lon': -68.4977255651657,
    #                            'radius': '916105.41237061098', 'uom': 'urn:ogc:def:uom:EPSG::9001',
    #                            'lat': 45.4430670070877}))



    # fail - _value_1=loc
    # find_service = find_service_element(location=loc,service=ser,
    #                                    serviceBoundary=serb, serviceBoundarySpecified=True, recursive=False,
    #                                    validateLocation=True)

        #removed items -  path=path, _value_1=via,



    #with out paramater names?
    # find_service = find_service_element(location, ser, xsd.SkipValue, True, xsd.SkipValue, False)

    # find_service = find_service_element(location, ser, path, uri, True, service_boundary, False)

    # All these varients fail 'str' object has no attribute 'keys'
    # find_service_element(_value_1={'location': location}, ser, xsd.SkipValue, xsd.SkipValue, True, xsd.SkipValue, False))
    # find_service = find_service_element(_value_1={'location': location, 'service': service, 'path': path})
    # find_service_element(_value_1={'location': location, 'service': service, 'path': path},validateLocation=True,serviceBoundary=serb,recursive=False)


    #Using InputDict
    t1['location'].append(location_array)
    t1['recursive'] = False
    t1['validateLocation'] = False

    find_service = find_service_element([location_array], ser, path, uri, True, service_boundary, False)


    return find_service

def _create_dictionary(dict_request):

    for key, value in dict_request.items():
        if type(value) is Circle:
            dict_request[key] = value.__dict__
            dict_request[key] = _create_dictionary(dict_request[key])

            dict_request['_value_1'] = dict_request.pop(key)

        elif type(value) is Location:
            dict_request[key] = value.__dict__
            dict_request[key] = _create_dictionary(dict_request[key])
            if key[0] == '_' and key[0] != '_value_1':
                dict_request[key[1:]] = dict_request.pop(key)
        else:
            if key[0] == '_' and key[0] != '_value_1':
                dict_request[key[1:]] = dict_request.pop(key)

    #Loop second time, seems like one item is skipped - TODO make this better
    flag_found = False
    for key, value in dict_request.items():
        if key[0] == '_' and key != '_value_1':
            dict_request[key[1:]] = dict_request.pop(key)
            flag_found = True

    if flag_found == True:
        _create_dictionary(dict_request)

    return dict_request

def _send_nenalog_response(nena_log_id, response_text, end_time, server_id):
    client = Client('http://localhost:52759/Logging.asmx?wsdl')

def create_NENA_log_events(request_text, query_type, start_time, response_text, end_time, server_id):
    # add query_ip_port, response_ip_port

    #Create Log ID used for both Request and Response
    nena_log_id = uuid.uuid4()

    _send_nenalog_request(nena_log_id, request_text, query_type, start_time, server_id)
    _send_nenalog_response(nena_log_id, response_text, end_time, server_id)
