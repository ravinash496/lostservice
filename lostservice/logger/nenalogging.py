from lxml import etree
import requests
import uuid

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


def create_NENA_log_events(request_text, query_type, start_time, response_text, end_time, server_id):
    # add query_ip_port, response_ip_port
    query_ip_port = '127.0.0.1:8080'
    response_ip_port = '127.0.0.1:8080'

    # Create Log ID used for both Request and Response
    nena_log_id = uuid.uuid4()

    is_valid_query = QUERYOTHER
    if (str.lower(query_type) == 'findservice') or (str.lower(query_type) == 'listservice') or (
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


    request_response = _send_nenalog_request(nena_log_id, request_text, query_type, start_time, server_id, query_ip_port, is_valid_query)
    response_response = _send_nenalog_response(nena_log_id, response_text, end_time, server_id, response_ip_port)

    #TODO LogResponse - if not 200 or always?


def _send_nenalog_request(nena_log_id, request_text, query_type, start_time, server_id, query_ip_port, is_valid_query):
    # Create the SOAP envelope.
    soap_env = etree.Element('{%s}Envelope' % SOAP_ENV_NS, nsmap=wrapper_nsmap)
    # Create the SOAP body.
    soap_body = etree.SubElement(soap_env, '{%s}Body' % SOAP_ENV_NS)
    # Now add the LogEventMessageRequest.
    log_event_message_req = etree.SubElement(soap_body, '{%s}LogEventMessageRequest' % LOG_EXCH_NS)

    # Create LogEventTimestamp
    log_event_timestamp = etree.SubElement(log_event_message_req, '{%s}LogEventTimestamp' % DATA_TYPES_NS)
    log_event_timestamp.text = str(start_time)

    # Create ElementID
    element_id = etree.SubElement(log_event_message_req, '{%s}ElementId' % DATA_TYPES_NS)
    element_id.text = server_id

    # Create EventValuesCode  -LoSTQuery
    event_value_code = etree.SubElement(log_event_message_req, '{%s}EventValuesCode' % CODE_LIST_NS)
    event_value_code.text = 'LoSTQuery'

    # Create OtherElementAddress  -queryIpAndPort
    # NENA Logging IP and Port-
    # NENA logging setting that specifies the IP Address and Port to be sent with LogEvents to the logging service.
    # This should be the public IP address and Port to access the ECRF/LVF.
    other_element_address = etree.SubElement(log_event_message_req, '{%s}OtherElementAddress' % CODE_LIST_NS)
    # TODO VB version uses Httpcontext to get IP and Port
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
        # Malformed query apply text to LogEventBody
        xml_request = etree.fromstring(request_text)
        log_event_body.append(xml_request)

    # Create DirectionValuesCodeType
    direction_values_code_type = etree.SubElement(log_event_body, '{%s}DirectionValuesCodeType' % CODE_LIST_NS)
    direction_values_code_type.text = 'incoming'

    print(etree.tostring(soap_env, pretty_print=True))

    #TODO replace URL with logging service setting
    r = requests.post("http://LP-DSTOICK-1:8088/mockLoggingBinding", data=etree.tostring(soap_env))

    print(r.text)

    return r


def _send_nenalog_response(nena_log_id, response_text, end_time, server_id, response_ip_port):

    # Create the SOAP envelope.
    soap_env = etree.Element('{%s}Envelope' % SOAP_ENV_NS, nsmap=wrapper_nsmap)
    # Create the SOAP body.
    soap_body = etree.SubElement(soap_env, '{%s}Body' % SOAP_ENV_NS)
    # Now add the LogEventMessageRequest.
    log_event_message_req = etree.SubElement(soap_body, '{%s}LogEventMessageRequest' % LOG_EXCH_NS)

    # Create LogEventTimestamp
    log_event_timestamp = etree.SubElement(log_event_message_req, '{%s}LogEventTimestamp' % DATA_TYPES_NS)
    log_event_timestamp.text = str(end_time)

    # Create ElementID
    element_id = etree.SubElement(log_event_message_req, '{%s}ElementId' % DATA_TYPES_NS)
    element_id.text = server_id

    # Create EventValuesCode  -LoSTResponse
    event_value_code = etree.SubElement(log_event_message_req, '{%s}EventValuesCode' % CODE_LIST_NS)
    event_value_code.text = 'LoSTResponse'

    other_element_address = etree.SubElement(log_event_message_req, '{%s}OtherElementAddress' % CODE_LIST_NS)
    # TODO VB version uses Httpcontext to get IP and Port
    other_element_address.text = response_ip_port

    # Create LogEventBody
    log_event_body = etree.SubElement(log_event_message_req, '{%s}LogEventBody' % DATA_TYPES_NS)

    # create LoSTQueryAdapter
    lost_query_adapter = etree.SubElement(log_event_body, '{%s}LoSTQueryAdapter' % DATA_TYPES_NS)

    # Create DirectionValuesCodeType
    direction_values_code_type = etree.SubElement(log_event_body, '{%s}DirectionValuesCodeType' % CODE_LIST_NS)
    direction_values_code_type.text = 'outgoing'

    # Now add the the response to the lost_query_adapter
    # (findService,listServicesByLocation,listServices, getServiceBoundary) ...
    xml_response = etree.fromstring(response_text)
    lost_query_adapter.append(xml_response)

    print(etree.tostring(soap_env, pretty_print=True))

    # TODO replace URL with logging service setting
    r = requests.post("http://LP-DSTOICK-1:8088/mockLoggingBinding", data=etree.tostring(soap_env))

    print(r.text)

    return r