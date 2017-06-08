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

    def __init__(self, context, converter, handler):
        """
        Constructor

        :param context: A reference to the lost context.
        :type context: :py:class:`lostservice.context.LostContext` 
        :param converter: A reference to an appropriate Converter instance.
        :type converter: A subclass of :py:class:`lostservice.converter.Converter`
        :param handler: A reference to an appropriate Hander instance.
        :type handler: A subclass of :py:class:`lostservice.handler.Handler`
        """
        self._context = context
        self._converter = converter
        self._handler = handler

    def run(self, data):
        """
        Runs the request through all the converters and handler.

        :param data: The request.
        :return: The response xml.
        """
        request = self._converter.parse(data)
        response = self._handler.handle_request(request, self._context)
        output = self._converter.format(response)

        return output

