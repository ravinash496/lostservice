#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. currentmodule:: nenalogging
.. moduleauthor:: Darell Stoick, Pat Blair  

Class to handle sending Logs to Logging Service(s)
"""


from lxml import etree
import requests
import uuid
from lostservice.configuration import general_logger
logger = general_logger()


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

QUERYVALID = 'valid'
QUERYMALFROMED = 'malformed'
QUERYOTHER = 'other'

SOAP_ENV_NS = 'http://schemas.xmlsoap.org/soap/envelope/'
LOG_EXCH_NS = 'urn:nena:xml:ns:LoggingExchange:2.0'
DATA_TYPES_NS = 'urn:nena:xml:ns:LoggingDataTypes:2.0'
CODE_LIST_NS = 'urn:nena:xml:ns:CodeList:2.0'
# Create the SOAP namespace map.
wrapper_nsmap = {
    'soap-env': SOAP_ENV_NS,
    'log-ex': LOG_EXCH_NS,
    'dt2': DATA_TYPES_NS,
    'cl2': CODE_LIST_NS
}


def create_NENA_log_events(request_text, query_type, start_time, response_text, end_time, conf):
    """
    Create and Send Request and Resposne to the list of configured logging service urls.
    :param request_text:  reqest 
    :param query_type: Type of Query
    :param start_time: UTC 
    :param response_text: response
    :param end_time:  UTC
    :param conf: configuration file
    :return: 
    """

    #get settings from ini file
    logging_service_urls = conf.get('Logging', 'logging_services', as_object=True, required=False)
    server_id = conf.get('Service', 'source_uri', as_object=False, required=False)

    # Check to see if Nena Loggging Service has been configured (optional)
    if len(logging_service_urls) < 1:
        logger.info('NENA Logging: No Service configured')
        return

    # add query_ip_port, response_ip_port  TODO get IP and Port
    query_ip_port = '127.0.0.1:8080'
    response_ip_port = '127.0.0.1:8080'

    # Create Log ID used for both Request and Response
    nena_log_id = 'urn:nena:uid:logEvent:%s' % str(uuid.uuid4())

    is_valid_query = QUERYOTHER
    if (str.lower(query_type) == 'findservice') or (str.lower(query_type) == 'listservices') or (
              str.lower(query_type) == 'listervicebylocation') or (str.lower(query_type) == 'getserviceboundary'):

        is_valid_query = QUERYVALID
    elif(str.lower(query_type) == QUERYMALFROMED):
        is_valid_query = QUERYMALFROMED
    else:
        is_valid_query = QUERYOTHER


    #Soap Structure
    #Envelope
     #Body
      #LogEventMessageRequest
        #LogEventTimestamp
        #LogEventBody
          #LoSTQueryAdapter
            #...Request or Response.
        #...
      #LogEventMessageRequest
     #Body
    #Envelope

    _send_nenalog_request(nena_log_id, request_text, start_time, server_id, query_ip_port, is_valid_query, logging_service_urls)
    _send_nenalog_response(nena_log_id, response_text, end_time, server_id, response_ip_port, logging_service_urls)

# End of create_NENA_log_events


def _send_nenalog_request(nena_log_id, request_text, start_time, server_id, query_ip_port, is_valid_query, logging_service_urls):
    """
    Send the Request
    :param nena_log_id: Log_Id
    :param request_text: request
    :param start_time: UTC
    :param server_id: Host Id
    :param query_ip_port: 
    :param is_valid_query: 
    :param logging_service_urls: nena log service Url
    :return: 
    """

    # Create the SOAP envelope.
    soap_env = etree.Element('{%s}Envelope' % SOAP_ENV_NS, nsmap=wrapper_nsmap)
    # Create the SOAP body.
    soap_body = etree.SubElement(soap_env, '{%s}Body' % SOAP_ENV_NS)
    # Now add the LogEventMessageRequest.
    log_event_message_req = etree.SubElement(soap_body, '{%s}LogEventMessageRequest' % LOG_EXCH_NS)

    # Create ElementID
    element_id = etree.SubElement(log_event_message_req, '{%s}ElementId' % DATA_TYPES_NS)
    element_id.text = server_id

    # Create LogEventTimestamp
    log_event_timestamp = etree.SubElement(log_event_message_req, '{%s}LogEventTimestamp' % DATA_TYPES_NS)
    log_event_timestamp.text = str(start_time)

    # Create EventValuesCode  -LoSTQuery
    event_value_code = etree.SubElement(log_event_message_req, '{%s}EventValuesCode' % CODE_LIST_NS)
    event_value_code.text = 'LoSTQuery'

    # Create OtherElementAddress  -queryIpAndPort
    # NENA Logging IP and Port-
    # NENA logging setting that specifies the IP Address and Port to be sent with LogEvents to the logging service.
    # This should be the public IP address and Port to access the ECRF/LVF.
    other_element_address = etree.SubElement(log_event_message_req, '{%s}OtherElementAddress' % CODE_LIST_NS)
    other_element_address.text = query_ip_port

    # Create LogEventBody
    log_event_body = etree.SubElement(log_event_message_req, '{%s}LogEventBody' % DATA_TYPES_NS)

    if (is_valid_query == QUERYVALID):
        # create LoSTQueryAdapter
        lost_query_adapter = etree.SubElement(log_event_body, '{%s}LoSTQueryAdapter' % DATA_TYPES_NS)

        # Now add the the request which will be one of these
        # (findService,listServicesByLocation,listServices, getServiceBoundary) to the lost_query_adapter...
        xml_request = etree.fromstring(request_text)
        lost_query_adapter.append(xml_request)

    elif(is_valid_query == QUERYMALFROMED):

        # create LoSTQueryAdapter
        lost_malformed_query = etree.SubElement(log_event_body, '{%s}LoSTMalformedQuery' % DATA_TYPES_NS)

        # Malformed query apply text to LogEventBody
        xml_request = etree.fromstring(request_text)
        lost_malformed_query.append(xml_request)

    # Create DirectionValuesCodeType
    direction_values_code_type = etree.SubElement(log_event_body, '{%s}DirectionValuesCodeType' % CODE_LIST_NS)
    direction_values_code_type.text = 'incoming'

    # Create LostQueryID
    lost_query_id = etree.SubElement(log_event_body, '{%s}LoSTQueryId' % DATA_TYPES_NS)
    lost_query_id.text = nena_log_id

    logger.info(etree.tostring(soap_env, pretty_print=True))

    for key, url in logging_service_urls.items():
        _post_nena_logging(soap_env, request_text, url)

# End of _send_nenalog_request


def _send_nenalog_response(nena_log_id, response_text, end_time, server_id, response_ip_port, logging_service_urls):
    """
    Send the Response
    :param nena_log_id: Log_Id
    :param response_text: response
    :param end_time:  end time UTC
    :param server_id: host Id
    :param response_ip_port:  
    :param logging_service_urls: nena log service Url
    :return: 
    """

    # Create the SOAP envelope.
    soap_env = etree.Element('{%s}Envelope' % SOAP_ENV_NS, nsmap=wrapper_nsmap)
    # Create the SOAP body.
    soap_body = etree.SubElement(soap_env, '{%s}Body' % SOAP_ENV_NS)
    # Now add the LogEventMessageRequest.
    log_event_message_req = etree.SubElement(soap_body, '{%s}LogEventMessageRequest' % LOG_EXCH_NS)

    # Create ElementID
    element_id = etree.SubElement(log_event_message_req, '{%s}ElementId' % DATA_TYPES_NS)
    element_id.text = server_id

    # Create LogEventTimestamp
    log_event_timestamp = etree.SubElement(log_event_message_req, '{%s}LogEventTimestamp' % DATA_TYPES_NS)
    log_event_timestamp.text = str(end_time)

    # Create EventValuesCode  -LoSTResponse
    event_value_code = etree.SubElement(log_event_message_req, '{%s}EventValuesCode' % CODE_LIST_NS)
    event_value_code.text = 'LoSTResponse'

    # Create OtherElementAddress  -queryIpAndPort
    other_element_address = etree.SubElement(log_event_message_req, '{%s}OtherElementAddress' % CODE_LIST_NS)
    other_element_address.text = response_ip_port

    # Create LogEventBody
    log_event_body = etree.SubElement(log_event_message_req, '{%s}LogEventBody' % DATA_TYPES_NS)

    # create LoSTQueryAdapter
    lost_query_adapter = etree.SubElement(log_event_body, '{%s}LoSTQueryAdapter' % DATA_TYPES_NS)

    # Create DirectionValuesCodeType
    direction_values_code_type = etree.SubElement(log_event_body, '{%s}DirectionValuesCodeType' % CODE_LIST_NS)
    direction_values_code_type.text = 'outgoing'

    # Create LostResponseID
    lost_resposne_id = etree.SubElement(log_event_body, '{%s}LoSTResponseId' % DATA_TYPES_NS)
    lost_resposne_id.text = nena_log_id


    # Now add the the response to the lost_query_adapter
    # (findService,listServicesByLocation,listServices, getServiceBoundary) ...
    xml_response = etree.fromstring(response_text)
    lost_query_adapter.append(xml_response)

    logger.info(etree.tostring(soap_env, pretty_print=True))

    for key, url in logging_service_urls.items():
        _post_nena_logging(soap_env, response_text, url)

# End of _send_nenalog_response


def _post_nena_logging(soap_env, raw_text, url):
    """

    :param soap_env: data to be logged includes request/response 
    :param raw_text: request/response
    :param url: url for nena logging
    :return:
    """

    try:
        requests.post(url, data=etree.tostring(soap_env))
        logger.debug('posting to Nena log')
    except Exception as e:
        logger.warning('%s :Raw Event: %s' % (str(e), raw_text))
# End of _post_nena_logging
