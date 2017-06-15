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
from lxml import etree
from injector import Module, provider, Injector, singleton
import lostservice.configuration as config
import lostservice.logging.auditlog as auditlog
import lostservice.db.gisdb as gisdb
import lostservice.queryrunner as queryrunner


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


class LostApplication(object):
    """
    The core LoST Application class.
    
    """
    def __init__(self, ctx=None):
        """
        Constructor
        
        :param context: Context information.
        :type context: :py:class:`lostservice.context.LostContext`
        """
        super(LostApplication, self).__init__()

        # Initialize the DI container.
        self._di_container = Injector([LostBindingModule()])

        # Set up the base logging, more will come from config later.
        self._logger = logging.getLogger('lostservice.app.LostApplication')
        self._logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        conf = self._di_container.get(config.Configuration)

        filehandler = logging.FileHandler(conf.get('Logging', 'logfile'))
        filehandler.setLevel(logging.DEBUG)
        filehandler.setFormatter(formatter)

        consolehandler = logging.StreamHandler()
        consolehandler.setLevel(logging.DEBUG)
        consolehandler.setFormatter(formatter)

        self._logger.addHandler(filehandler)
        self._logger.addHandler(consolehandler)

        self._converter_template = conf.get('ClassLookupTemplates', 'converter_template')
        self._handler_template = conf.get('ClassLookupTemplates', 'handler_template')

        # TODO: Set up auditors
        auditor = self._di_container.get(auditlog.AuditLog)

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

        self._logger.debug(response)
        self._logger.info('Finished LoST query execution . . .')

        return response


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    # parser.add_argument('config', help='the path to the configuration file.')
    parser.add_argument('request', help='the path to a file containing a LoST request')
    args = parser.parse_args()

    request = None
    with open(args.request, 'r') as request_file:
        request = request_file.read()

    lost_app = LostApplication()
    context = {}
    response = lost_app.execute_query(request, context)
    print(response)



