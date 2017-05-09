#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. currentmodule:: lostservice.handling.getserviceboundary
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

Handler(s) for getServiceBoundary requests
"""

from lostservice.handler import Handler


class GetServiceBoundaryHandler(Handler):
    """
    Base getServiceBoundary request handler.
    """

    def __init__(self):
        """
        Constructor
        """
        super(GetServiceBoundaryHandler, self).__init__()

    def handle_request(self, request):
        """
        Entry point for request handling.

        :param request: The request
        :type request: A subclass of :py:class:`GetServiceBoundaryRequest`
        :return: The response.
        :rtype: A subclass of :py:class:`GetServiceBoundaryResponse`
        """
        raise NotImplementedError("Can't handle getServiceBoundary requests just yet, come back later.")
