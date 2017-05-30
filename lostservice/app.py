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
import lostservice.context as context
import lostservice.queryrunner as queryrunner

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

        # The context can either be passed in or built from
        # the environment.
        if ctx is not None:
            self._context = ctx
        else:
            # The context can take params to the constructor, but we're going to
            # assume it can pull from the environment for now.
            self._context = context.LostContext()

        # Set up the base logging, more will come from config later.
        self._logger = logging.getLogger('lostservice.app.LostApplication')
        self._logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        filehandler = logging.FileHandler(self._context.configuration.get('Logging', 'logfile'))
        filehandler.setLevel(logging.DEBUG)
        filehandler.setFormatter(formatter)

        consolehandler = logging.StreamHandler()
        consolehandler.setLevel(logging.DEBUG)
        consolehandler.setFormatter(formatter)

        self._logger.addHandler(filehandler)
        self._logger.addHandler(consolehandler)

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
        converter_name = 'lostservice.converting.xml.{0}XmlConverter'.format(base_name)
        handler_name = 'lostservice.handling.core.{0}Handler'.format(base_name)

        # Get a reference to the converter class and create an instance.
        ConverterClass = self._get_class(converter_name)
        converter = ConverterClass()

        # Get a reference to the handler class and create an instance.
        HandlerClass = self._get_class(handler_name)
        handler = HandlerClass()

        runner = queryrunner.QueryRunner(self._context, converter, handler)

        return runner

    def _execute_internal(self, queryrunner, data):
        """
        Executes a query by calling the query runner.
        
        :param queryrunner: A queryrunner set up for the given query. 
        :param data: The query as and element tree.
        :return: The query response as an element tree.
        """
        return queryrunner.run(data)

    def execute_query(self, data):
        """
        Executes a given LoST query.

        :param data: The LoST query request XML.
        :type data: ``str``
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
        parsed_response = self._execute_internal(runner, parsed_request)

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

    custom_ini_file = os.path.join(os.path.dirname(__file__), './lostservice.ini')
    os.environ[context._CONFIGFILE] = custom_ini_file

    request = None
    with open(args.request, 'r') as request_file:
        request = request_file.read()

    lost_app = LostApplication()
    response = lost_app.execute_query(request)
    print(response)
    os.environ.pop(context._CONFIGFILE)



