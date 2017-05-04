#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: app
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

The main entry point for ECRF/LVF services.
"""

import argparse


class LostApplication(object):
    """
    The core LoST Application class.
    
    """
    def __init__(self, config):
        """
        Constructor
        
        :param config: The configuration information for the app.
        :type config: ``dict``
        """
        super(LostApplication, self).__init__()
        self._config = config

    def execute_query(self, data):
        """
        Executes a given LoST query.
        
        :param data: The LoST query request XML.
        :type data: ``str``
        :return: The LoST query response XML.
        :rtype: ``str``
        """
        # generally every request will be routed to
        # 1) the parser
        # 2) the dispatcher
        # 3) the formatter
        raise NotImplementedError("Not implemented.")


def configure(config_file):
    """
    Load up configuration information.
    
    :return: A dictionary of configuration options.
    :rtype: ``dict``
    """
    print(config_file)
    return {'someKey': 'some value'}


def run(config, request):
    """
    Run the app to process a request.
    
    :param config: The configuration information for the application.
    :type config: ``dict``
    :param request: The request to process.
    :type request: ``str``
    :return: None
    :rtype: None
    """
    # Create the service object that will actually do the work of the application. (This could be done in a web app,
    # or from a command line app, etc.)
    service_obj = LostApplication(config)
    response = service_obj.execute_query(request)
    print(response)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('config', help='the path to the configuration file.')
    parser.add_argument('request', help='the path to a file containing a LoST request')
    args = parser.parse_args()

    print(args.config)
    print(args.request)

    _config = configure(args.config)
    run(_config, args.request)


