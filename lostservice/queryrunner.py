#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: queryrunner
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

A coordinator/runner for orchestrating the various steps of LoST
queries.
"""


class QueryRunner(object):
    """
    A class for executing a single LoST Query, handles routing to 
    given converter and handler as well as logging and overall error
    handling.
    """

    def __init__(self, converter, handler):
        """
        Constructor

        :param converter: A reference to an appropriate Converter instance.
        :type converter: A subclass of :py:class:`lostservice.converter.Converter`
        :param handler: A reference to an appropriate Hander instance.
        :type handler: A subclass of :py:class:`lostservice.handler.Handler`
        """
        self._converter = converter
        self._handler = handler

    def run(self, data, context):
        """
        Runs the request through all the converters and handler.

        :param data: The request.
        :type data:
        :param context: The request context.
        :type context: ``dict``
        :return: The response xml.
        """
        request = self._converter.parse(data)
        response = self._handler.handle_request(request, context)
        output = self._converter.format(response)

        return output

