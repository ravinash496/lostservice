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
from logging.config import dictConfig
import datetime
import pytz
import socket
import sys
import uuid
from lxml import etree
from injector import Module, provider, Injector, singleton
from sqlalchemy.engine import Engine
from sqlalchemy import create_engine
import civvy.db.postgis.query as civvy_pg
import lostservice.configuration as config
import lostservice.logger.auditlog as auditlog
import lostservice.logger.transactionaudit as txnaudit
import lostservice.logger.diagnosticsaudit as diagaudit
import lostservice.db.gisdb as gisdb
import lostservice.queryrunner as queryrunner
import lostservice.logger.nenalogging as nenalog
import lostservice.exception as exp
from lostservice.configuration import general_logger
import asyncio
import functools
from threading import Thread

logger = general_logger()


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

    @singleton
    @provider
    def provide_pg_query_executor(self, config: config.Configuration) -> civvy_pg.PgQueryExecutor:
        """
        Provider function for a PGQueryExecutor.

        :param config: The config object.
        :return:
        """
        host = config.get('Database', 'host')
        port = config.get('Database', 'port')
        db_name = config.get('Database', 'dbname')
        username = config.get('Database', 'username')
        password = config.get('Database', 'password')
        return civvy_pg.PgQueryExecutor(host=host, port=port, database=db_name, user=username, password=password)

    @singleton
    @provider
    def provide_sqlalchemy_engine(self, config: config.Configuration) -> Engine:
        """
        Provider function for SQLAlchemhy Engine.

        :param config:
        :return:
        """
        return create_engine(config.get_gis_db_connection_string())


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
        self.audit_logging_enabled = conf.get_logging_db_connection_string()

        if conf.get_logging_db_connection_string():
            transaction_listener = txnaudit.TransactionAuditListener(conf)
            auditor.register_listener(transaction_listener)
            diagnostic_listener = diagaudit.DiagnosticAuditListener(conf)
            auditor.register_listener(diagnostic_listener)

        self.nena_logging_enabled = conf.get('Logging', 'logging_services')

        # setup a loop so logging can happen asynchronously - in order not to interfere with the web.py asyncio loop
        # start it on another thread - see execute_query (call_soon_threadsafe) to see it in action
        self.loop = asyncio.new_event_loop()
        t = Thread(target=self.start_logging_event_loop, args=(self.loop,))
        t.start()

    def start_logging_event_loop(self, loop):
        """
        start up an event loop so that logging can be called asynchronously
        :param loop:
        :return:
        """
        asyncio.set_event_loop(loop)
        loop.run_forever()

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

        conf = self._di_container.get(config.Configuration)
        parsed_request = None
        response = None
        parsed_response = None
        endtime = None

        activity_id = str(uuid.uuid4())
        starttime = datetime.datetime.now(tz=pytz.utc)

        try:
            logger.info('Starting LoST query execution. . .')
            # Here's what's gonna happen . . .
            # 1. Parse the request and pull out the root element.
            parsed_request = etree.fromstring(data)
            logger.debug(parsed_request)
            qname = etree.QName(parsed_request)
            query_name = qname.localname

            # 2. call _build_queryrunner to get the runner.
            runner = self._build_queryrunner(query_name)

            # 3. call _execute_internal to process the request.
            parsed_response = self._execute_internal(runner, parsed_request, context)

            # 4. serialize the xml back out into a string and return it.
            response = etree.tostring(parsed_response['response'])

            # Create End Time (response has been sent)
            endtime = datetime.datetime.now(tz=pytz.utc)

            # TODO Identify Malformed Query Types
            # Send Logs to configured NENA Logging Services

            logger.debug(response)
            logger.info('Finished LoST query execution. . .')

        except Exception as e:
            logger.error(e)
            endtime = datetime.datetime.now(tz=pytz.utc)
            source_uri = conf.get('Service', 'source_uri', as_object=False, required=False)
            if isinstance(e, exp.RedirectException):
                logger.error(f'Redirect Exception: {e}')
                response = exp.build_redirect_response(e, source_uri)
            elif isinstance(e, etree.LxmlError):
                logger.error(f'Malformed XML request: {e} Source URI: {source_uri}')
                response = exp.build_error_response(exp.BadRequestException('Malformed request xml.', None), source_uri)
            elif isinstance(e, exp.NotFoundException):
                response = exp.build_error_response(e, source_uri)
            else:
                response = exp.build_error_response(e, source_uri)
            self._audit_diagnostics(activity_id, e)
        finally:
            if parsed_response is None:
                if response is not None:
                    logger.debug('There was no found parsed response. Adding a blank one into record.')
                    parsed_response = {'response': etree.fromstring(response.encode()),
                                       'latitude': 0.0,
                                       'longitude': 0.0
                    }
            if self.audit_logging_enabled:
                logger.debug('Audit Logging: Begin')
                self.loop.call_soon_threadsafe(functools.partial(self._audit_transaction,
                                                                 activity_id,
                                                                 parsed_request,
                                                                 starttime,
                                                                 parsed_response['response'],
                                                                 endtime, context,
                                                                 parsed_response['latitude'],
                                                                 parsed_response['longitude']))
            if self.nena_logging_enabled:
                self.loop.call_soon_threadsafe(
                    functools.partial(nenalog.create_NENA_log_events, data, query_name, starttime, response, endtime,
                                      conf))

            logger.debug('Audit Logging: Complete')
        return response

    def _audit_transaction(self, activity_id, parsed_request, start_time, parsed_response, end_time, context,
                           latitude=0, longitude=0):
        """
        Create and send the request and response to the transactionlogs
        :param activity_id:
        :param parsed_request
        :param start_time:
        :param parsed_response:
        :param end_time:
        :param context:
        :param: latitude
        :param: longitude
        :return:
        """
        logger.debug('Audit Transaction: Begin')
        nslookup = {'ls': 'urn:ietf:params:xml:ns:lost1'}

        auditor = self._di_container.get(auditlog.AuditLog)
        conf = self._di_container.get(config.Configuration)
        server_id = conf.get('Service', 'source_uri', as_object=False, required=False)
        logger.debug('Creating transaction event. . .')
        trans = txnaudit.TransactionEvent()
        trans.activity_id = activity_id
        trans.start_time_utc = start_time
        trans.end_time_utc = end_time
        trans.transaction_ms = int((end_time - start_time).microseconds * .001)
        trans.server_id = server_id
        trans.machine_id = socket.gethostname()
        trans.client_id = context['web_ctx'].client_ip if 'web_ctx' in context else ''
        trans.request_loc_x = longitude
        trans.request_loc_y = latitude

        if parsed_request is not None:
            trans.request = etree.tostring(parsed_request, encoding='unicode')
            req_service_urn = parsed_request.xpath('//ls:service/text()', namespaces=nslookup)
            if req_service_urn is not None and len(req_service_urn) > 0:
                trans.request_svc_urn = req_service_urn[0]

            qname = etree.QName(parsed_request)
            request_type = "LoST" + str(qname.localname)
            trans.request_type = request_type

            loc_type = parsed_request.xpath('//ls:location/@profile', namespaces=nslookup)
            trans.request_loc_type = loc_type[0] if loc_type else ''

            request_loc = parsed_request.xpath('//ls:location', namespaces=nslookup)
            trans.request_loc = etree.tostring(request_loc[0][0], encoding='unicode') \
                if len(request_loc) > 0 and len(request_loc[0]) > 0 else ''

        if parsed_response is not None:
            trans.response = etree.tostring(parsed_response, encoding='unicode')
            qname = etree.QName(parsed_response)
            trans.response_type = "LoST" + str(qname)

            error_type = parsed_response.xpath('//ls:errors', namespaces=nslookup)
            trans.response_error_type = etree.QName(error_type[0][0]).localname \
                if len(error_type) > 0 and len(error_type[0]) > 0 else ''

        # TODO: need to update this when we get to recursion.
        trans.response_src_type = 'Local'

        auditor.record_event(trans)
        logger.debug('Audit Transaction: Complete')
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
        logger.debug('Audit Diagnostics: Begin')
        diag = diagaudit.DiagnosticEvent()
        diag.qps_log_id = -1
        diag.event_id = 1
        diag.priority = 5
        diag.severity = 2
        diag.activity_id = activity_id
        diag.category_name = "Diagnostic"
        diag.title = "Error"
        diag.timestamp_utc = datetime.datetime.now(tz=pytz.utc).strftime('%m/%d/%Y %H:%M:%S %Z%z')
        diag.machine_name = socket.gethostname()
        diag.server_id = server_id
        diag.machine_id = diag.machine_name
        diag.message = str(error)
        diag.formatted_message = 'Timestamp: {0} Message: {1}'.format(diag.timestamp_utc, error)

        auditor.record_event(diag)
        logger.debug('Audit Diagnostics: Complete')

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


