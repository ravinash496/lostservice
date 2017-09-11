#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: app
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

The main entry point for ECRF/LVF services.
"""

import os
import argparse
import logging
from logging.handlers import RotatingFileHandler
import datetime
import pytz
import socket
import uuid
from lxml import etree
from injector import Module, provider, Injector, singleton
import lostservice.configuration as config
import lostservice.logger.auditlog as auditlog
import lostservice.logger.transactionaudit as txnaudit
import lostservice.logger.diagnosticsaudit as diagaudit
import lostservice.db.gisdb as gisdb
import lostservice.queryrunner as queryrunner
import lostservice.logger.nenalogging as nenalog
import lostservice.exception as exp


class LostBindingModule(Module):
    """
    Binding specifications for the IOC container.

    """
    @singleton
    @provider
    def provide_config(self) -> config.Configuration:
        """
        Provider function for config.

        :return: The config object.
        :rtype: :py:class:`lostservice.configuration.Configuration`
        """
        return config.Configuration()

    @singleton
    @provider
    def provide_auditor(self) -> auditlog.AuditLog:
        """
        Provider function for auditing.

        :return: The auditlog object.
        :rtype: :py:class:`lostservice.logging.auditlog.AuditLog`
        """
        return auditlog.AuditLog()

    @provider
    def provide_db_wrapper(self, config: config.Configuration) -> gisdb.GisDbInterface:
        """
        Provider function for the database interface.

        :return: An instance of the db interface object.
        :rtype: :py:class:`lostservice.db.gisdb.GisDbInterface`
        """
        return gisdb.GisDbInterface(config)


class WebRequestContext(object):
    """
    Container for web request information from the web server.

    """
    def __init__(self, client_ip=None):
        """
        Constructor.

        """
        super(WebRequestContext, self).__init__()
        self._client_ip = client_ip

    @property
    def client_ip(self):
        """
        Property for the client IP address.

        :return: The IP address of the client that initiated the web service request.
        :rtype: ``str``
        """
        return self._client_ip

    @client_ip.setter
    def client_ip(self, value):
        self._client_ip = value


class LostApplication(object):
    """
    The core LoST Application class.
    
    """
    def __init__(self):
        """
        Constructor

        """
        super(LostApplication, self).__init__()

        # Initialize the DI container.
        self._di_container = Injector([LostBindingModule()])

        # Set up the base logging, more will come from config later.
        self._logger = logging.getLogger('lostservice.app.LostApplication')
        self._logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        conf = self._di_container.get(config.Configuration)

        logfile = conf.get('Logging', 'logfile')
        filehandler = RotatingFileHandler(logfile, mode='a', maxBytes=10 * 1024 * 1024,
                                             backupCount=2, encoding=None, delay=0)
        filehandler.setLevel(logging.DEBUG)
        filehandler.setFormatter(formatter)

        consolehandler = logging.StreamHandler()
        consolehandler.setLevel(logging.DEBUG)
        consolehandler.setFormatter(formatter)

        self._logger.addHandler(filehandler)
        self._logger.addHandler(consolehandler)

        self._converter_template = conf.get('ClassLookupTemplates', 'converter_template')
        self._handler_template = conf.get('ClassLookupTemplates', 'handler_template')

        auditor = self._di_container.get(auditlog.AuditLog)
        if conf.get_logging_db_connection_string():
            transaction_listener = txnaudit.TransactionAuditListener(conf)
            auditor.register_listener(transaction_listener)
            diagnostic_listener = diagaudit.DiagnosticAuditListener(conf)
            auditor.register_listener(diagnostic_listener)

    def _get_class(self, classname):
        """
        Creates an instance of the class with the given name.
        Credit to 
        https://stackoverflow.com/questions/452969/does-python-have-an-equivalent-to-java-class-forname
        
        :param classname: The fully qualified name of the class. 
        :return: A instance of that class.
        """
        parts = classname.split('.')
        root_module = '.'.join(parts[:-1])
        m = __import__(root_module)
        for comp in parts[1:]:
            m = getattr(m, comp)
        return m

    def _build_queryrunner(self, query_name):
        """
        Builds a query runner object for the given query.
        
        :param query_name: The name of the query to be executed.
        :return: :py:class:`lostservice.app.QueryRunner`
        """
        base_name = query_name[0].upper() + query_name[1:]

        # All of the classes for converters and handlers are in known packages
        # and follow a naming convention of the form [lost request name]XmlConverter
        # and [lost request name]Handler respectively.  Given the name of the query,
        # we can create instances of those classes dynamically.

        converter_name = self._converter_template.format(base_name)
        handler_name = self._handler_template.format(base_name)

        # Get a reference to the converter class and create an instance.
        ConverterClass = self._get_class(converter_name)
        converter = self._di_container.get(ConverterClass)

        # Get a reference to the handler class and create an instance.
        HandlerClass = self._get_class(handler_name)
        handler = self._di_container.get(HandlerClass)

        runner = queryrunner.QueryRunner(converter, handler)

        return runner

    def _execute_internal(self, queryrunner, data, context):
        """
        Executes a query by calling the query runner.

        :param queryrunner: A queryrunner set up for the given query.
        :param data: The query as and element tree.
        :param context: The request context.
        :type context: ``dict``
        :return: The query response as an element tree.
        """
        return queryrunner.run(data, context)

    def execute_query(self, data, context):
        """
        Executes a given LoST query.

        :param data: The LoST query request XML.
        :type data: ``str``
        :param context: The request context.
        :type context: ``dict``
        :return: The LoST query response XML.
        :rtype: ``str``
        """
        self._logger.info('Starting LoST query execution . . .')
        self._logger.debug(data)

        conf = self._di_container.get(config.Configuration)
        parsed_request = None
        response = None
        parsed_response = None
        endtime = None

        activity_id = str(uuid.uuid4())
        starttime = datetime.datetime.now(tz=pytz.utc)

        try:
            # Here's what's gonna happen . . .
            # 1. Parse the request and pull out the root element.
            parsed_request = etree.fromstring(data)
            qname = etree.QName(parsed_request)
            query_name = qname.localname

            # 2. call _build_queryrunner to get the runner.
            runner = self._build_queryrunner(query_name)

            # 3. call _execute_internal to process the request.
            parsed_response = self._execute_internal(runner, parsed_request, context)

            # 4. serialize the xml back out into a string and return it.
            response = etree.tostring(parsed_response)

            # Create End Time (response has been sent)
            endtime = datetime.datetime.now(tz=pytz.utc)

            # TODO Identify Malformed Query Types
            # Send Logs to configured NENA Logging Services
            nenalog.create_NENA_log_events(data, query_name, starttime, response, endtime, conf)

            self._logger.debug(response)
            self._logger.info('Finished LoST query execution . . .')

        except Exception as e:
            endtime = datetime.datetime.now(tz=pytz.utc)
            self._audit_diagnostics(activity_id, e)
            self._logger.error(e)
            source_uri = conf.get('Service', 'source_uri', as_object=False, required=False)
            if isinstance(e, etree.LxmlError):
                response = exp.build_error_response(exp.BadRequestException('Malformed request xml.', None), source_uri)
            else:
                response = exp.build_error_response(e, source_uri)
        finally:
            if parsed_response is None:
                parsed_response = etree.fromstring(response.encode())
            self._audit_transaction(activity_id, parsed_request, starttime, parsed_response, endtime, context)

        return response

    def _audit_transaction(self, activity_id, parsed_request, start_time, parsed_response, end_time, context):
        """
        Create and send the request and response to the transactionlogs
        :param request:
        :param start_time:
        :param response_text:
        :param end_time:
        :return:
        """
        nslookup = {'ls':'urn:ietf:params:xml:ns:lost1'}

        auditor = self._di_container.get(auditlog.AuditLog)
        conf = self._di_container.get(config.Configuration)
        server_id = conf.get('Service', 'source_uri', as_object=False, required=False)

        trans = txnaudit.TransactionEvent()
        trans.activityid = activity_id
        trans.starttimeutc = start_time
        trans.endtimeutc = end_time
        trans.transactionms = int((start_time - end_time).microseconds * .001)
        trans.serverid = server_id
        trans.machineid = socket.gethostname()
        trans.clientid = context['web_ctx'].client_ip if 'web_ctx' in context else ''

        if parsed_request is not None:
            trans.request = etree.tostring(parsed_request, encoding='unicode')
            req_service_urn = parsed_request.xpath('//ls:service/text()', namespaces=nslookup)
            if req_service_urn is not None and len(req_service_urn) > 0:
                trans.requestsvcurn = req_service_urn[0]

            qname = etree.QName(parsed_request)
            request_type = "LoST" + str(qname.localname)
            trans.requesttype = request_type

            loc_type = parsed_request.xpath('//ls:location/@profile', namespaces=nslookup)
            trans.requestloctype = loc_type[0] if loc_type else ''

            requestloc = parsed_request.xpath('//ls:location', namespaces=nslookup)
            trans.requestloc = etree.tostring(requestloc[0][0], encoding='unicode') \
                if len(requestloc) > 0 and len(requestloc[0]) > 0 else ''

        if parsed_response is not None:
            trans.response = etree.tostring(parsed_response, encoding='unicode')
            qname = etree.QName(parsed_response)
            trans.responsetype = "LoST" + str(qname)

            error_type = parsed_response.xpath('//ls:errors', namespaces=nslookup)
            trans.responseerrortype = etree.QName(error_type[0][0]).localname \
                if len(error_type) > 0 and len(error_type[0]) > 0 else ''

        # TODO: need to update this when we get to recursion.
        trans.responsesrctype = 'Local'

        auditor.record_event(trans)

    def _audit_diagnostics(self, activity_id, error):
        """
        Create and send the request and response to the transactionlogs
        :param request:
        :param start_time:
        :param response_text:hv
        :param end_time:
        :return:
        """
        auditor = self._di_container.get(auditlog.AuditLog)

        conf = self._di_container.get(config.Configuration)
        server_id = conf.get('Service', 'source_uri', as_object=False, required=False)

        diag = diagaudit.DiagnosticEvent()
        diag.qpslogid = -1
        diag.eventid = 1
        diag.priority = 5
        diag.severity = 2
        diag.activityid = activity_id
        diag.categoryname = "Diagnostic"
        diag.title = "Error"
        diag.timestamputc = datetime.datetime.now(tz=pytz.utc).strftime('%m/%d/%Y %H:%M:%S %Z%z')
        diag.machinename = socket.gethostname()
        diag.serverid = server_id
        diag.machineid = diag.machinename
        diag.message = str(error)
        diag.formattedmessage = 'Timestamp: {0} Message: {1}'.format(diag.timestamputc, error)

        auditor.record_event(diag)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    # parser.add_argument('config', help='the path to the configuration file.')
    parser.add_argument('request', help='the path to a file containing a LoST request')
    args = parser.parse_args()
    custom_ini_file = os.path.join(os.path.dirname(__file__), './lostservice.ini')
    os.environ['CONFIGFILE'] = custom_ini_file

    request = None
    with open(args.request, 'r') as request_file:
        request = request_file.read()

    lost_app = LostApplication()
    context = {}
    response = lost_app.execute_query(request, context)

    if type(response) is str:
        print(response)
    else:
        print(response.decode("utf-8"))


