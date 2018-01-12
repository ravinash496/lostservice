#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. currentmodule:: nenalogging
.. moduleauthor:: Darell Stoick, Pat Blair  

Class to handle sending Logs to Logging Service(s)
"""

import uuid
import asyncio
import aiohttp

from lxml import etree
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
    Create and Send Request and Response to the list of configured logging service urls.
    :param request_text: 
    :param query_type: 
    :param start_time: UTC
    :param response_text: 
    :param end_time:  UTC
    :param conf: 
    :return: 
    """
    logger.debug('Create NENA Log Events: Begin')
    #get settings from ini file
    logging_service_urls = conf.get('Logging', 'logging_services', as_object=True, required=False)
    # Check to see if NENA Logging Service has been configured (optional)
    if len(logging_service_urls) < 1:
        logger.info('NENA Logging: No Service configured')
        return

    server_id = conf.get('Service', 'source_uri', as_object=False, required=False)
    # add query_ip_port, response_ip_port  TODO get IP and Port
    query_ip_port = '127.0.0.1:8080'
    response_ip_port = '127.0.0.1:8080'

    # Create Log ID used for both Request and Response
    nena_log_id = 'urn:nena:uid:logEvent:%s' % str(uuid.uuid4())

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
    _send_nenalog_request(nena_log_id, request_text,
                          start_time, server_id,
                          query_ip_port, is_valid_query,
                          logging_service_urls)
    _send_nenalog_response(nena_log_id, response_text,
                           end_time, server_id,
                           response_ip_port, logging_service_urls)

    logger.debug('Create NENA Log Events: Complete')

def _send_nenalog_request(nena_log_id, request_text, start_time, server_id,
                          query_ip_port, is_valid_query, logging_service_urls):
    """
    Send the Request
    :param nena_log_id: 
    :param request_text: 
    :param start_time: 
    :param server_id: 
    :param query_ip_port: 
    :param is_valid_query: 
    :param logging_service_urls: 
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

    logger.debug(etree.tostring(soap_env, pretty_print=True))

    logger.info('Calling NENA Logging Service')
    futures = [_post_async_nena_logging(soap_env, request_text, url) for key, url in logging_service_urls.items()]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(futures))
    logger.info('NENA Logging for Request Complete')

def _send_nenalog_response(nena_log_id, response_text, end_time, server_id, response_ip_port, logging_service_urls):
    """
    Send the Response
    :param nena_log_id: 
    :param response_text: 
    :param end_time: 
    :param server_id: 
    :param response_ip_port: 
    :param logging_service_urls: 
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

    logger.debug(etree.tostring(soap_env, pretty_print=True))

    futures = [_post_async_nena_logging(soap_env, response_text, url) for key, url in logging_service_urls.items()]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(futures))

# End of _send_nenalog_response

async def _post_async_nena_logging(soap_env, raw_text, url):
    """
    Async Post to the logging service
    :param soap_env: 
    :param raw_text: 
    :param url: 
    :return: 
    """

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, data=etree.tostring(soap_env)) as response:
                if response.status != 200:
                    print('NENA Logging Failure: %s :Raw Event: %s' % (response.text, raw_text))

        except Exception as e:
            print('%s :Raw Event: %s' % (str(e), raw_text))
        #TODO Log Error(s)

# End of _post_async_nena_logging