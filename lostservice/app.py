#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: app
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

The main entry point for ECRF/LVF services.
"""

import argparse
import configparser
import logging
from joblib import Parallel, delayed
from lostservice.converter import ParseException, FormatException


class LostApplication(object):
    """
    The core LoST Application class.
    
    """
    def __init__(self, config):
        """
        Constructor
        
        :param config: The configuration information for the app.
        :type config: ``ConfigParser``
        """
        super(LostApplication, self).__init__()
        self._config = config

        self._logger = logging.getLogger('lostservice.app.LostApplication')
        self._logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        filehandler = logging.FileHandler(self._config.get('Logging', 'LogFile'))
        filehandler.setLevel(logging.DEBUG)
        filehandler.setFormatter(formatter)

        consolehandler = logging.StreamHandler()
        consolehandler.setLevel(logging.DEBUG)
        consolehandler.setFormatter(formatter)

        self._logger.addHandler(filehandler)
        self._logger.addHandler(consolehandler)

        self._converters = self._config.get('Converters', 'ConverterClasses').split(',')
        self._handlers = self._config.get('Handlers', 'HandlerClasses').split(',')

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

        response = None

        # convs = Parallel(n_jobs=4)(delayed(_get_class)(name) for name in self._converters)
        # print(convs)

        model = Parallel(n_jobs=4)(delayed(_try_parse_request)(name, data) for name in self._converters)
        print(model)

        self._logger.debug(response)
        self._logger.info('Finished LoST query execution . . .')

        return response


def _try_parse_request(convertername, data):
    """
    Wrapper for trying request parsing.
    
    :param convertername: The name of the converter class to try.
    :type convertername: ``str``
    :param data: The data to parse.
    :type data: ``str``
    :return: The parsed request.
    :rtype: A subclass of :py:class:`lostapplication.model.requests.Request`
    """
    retval = None
    try:
        # self._logger.debug('Attempting parse with {convertername}', convertername)

        converterclass = _get_class(convertername)
        converter = converterclass()
        if converter is not None:
            retval = converter.parse(data)
    except ParseException:
        # self._logger.error('Parse failed')
        pass

    return retval


def _try_format_response(convertername, data):
    """
    Wrapper for trying to format a response.

    :param convertername: The name of the converter class to try.
    :type convertername: ``str``
    :param data: The data to format.
    :type data: A subclass of :py:class:`lostapplication.model.responses.Response`
    :return: The formatted response.
    :rtype: ``str``
    """
    retval = None
    try:
        # self._logger.debug('Attempting format with {convertername}', convertername)

        converterclass = _get_class(convertername)
        converter = converterclass()
        if converter is not None:
            retval = converter.parse(data)
    except FormatException:
        # self._logger.error('Format failed')
        pass

    return retval


def _get_class(name):
    """
    Creates in instance of the named class.

    :param name: The name of the class to create. 
    :type name: ``str``
    :return: An new instance of the named class.
    """
    # http://stackoverflow.com/questions/452969/does-python-have-an-equivalent-to-java-class-forname
    parts = name.split('.')
    themodule = ".".join(parts[:-1])
    m = __import__(themodule)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m


def configure(config_file):
    """
    Load up configuration information.
    
    :return: A dictionary of configuration options.
    :rtype: ``ConfigParser``
    """
    config = configparser.ConfigParser()
    config.read(config_file)
    return config


def run(config, request):
    """
    Run the app to process a request.
    
    :param config: The configuration information for the application.
    :type config: ``ConfigParser``
    :param request: The request to process.
    :type request: ``str``
    :return: None
    :rtype: None
    """
    # Create the service object that will actually do the work of the application. (This could be done in a web app,
    # or from a command line app, etc.)
    lost_app = LostApplication(config)
    response = lost_app.execute_query(request)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('config', help='the path to the configuration file.')
    parser.add_argument('request', help='the path to a file containing a LoST request')
    args = parser.parse_args()

    _request_data = None
    with open(args.request, 'r') as request_file:
        _request_data = request_file.read()

    _config = configure(args.config)
    run(_config, _request_data)


