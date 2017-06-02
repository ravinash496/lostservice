#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. currentmodule:: lostservice.handling..findservice
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

Handler(s) for findService requests
"""

from lostservice.handler import Handler


class FindServiceHandler(Handler):
    """
    Base findService request handler.
    """

    def __init__(self):
        """
        Constructor
        """
        super(FindServiceHandler, self).__init__()

    def handle_request(self, request, context):
        """
        
        :param request: 
        :param context: The context.
        :type context: :py:class:`lostservice.context.LostContext`
        :return: 
        """
        """
        Entry point for request handling.

        :param request: The request
        :type request: A subclass of :py:class:`FindServiceRequest`
        :return: The response.
        :rtype: A subclass of :py:class:`FindServiceResponse`
        """
        # raise NotImplementedError("Can't handle findService requests just yet, come back later.")
