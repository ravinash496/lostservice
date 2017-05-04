#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. currentmodule:: lostservice.handling.listservices
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

Handler(s) for listServices* requests
"""

from lostservice.handler import Handler


class ListServicesHandler(Handler):
    """
    Base listServices request handler.
    """

    def __init__(self):
        """
        Constructor
        """
        super(ListServicesHandler, self).__init__()

    def handle_request(self, request):
        """
        Entry point for request handling.

        :param request: The request
        :type request: A subclass of :py:class:`ListServicesRequest`
        :return: The response.
        :rtype: A subclass of :py:class:`ListServicesResponse`
        """
        raise NotImplementedError("Can't handle listServices requests just yet, come back later.")


class ListServicesByLocationHandler(Handler):
    """
    Base listServicesByLocation request handler.
    """

    def __init__(self):
        """
        Constructor
        """
        super(ListServicesByLocationHandler, self).__init__()

    def handle_request(self, request):
        """
        Entry point for request handling.

        :param request: The request
        :type request: A subclass of :py:class:`ListServicesByLocationRequest`
        :return: The response.
        :rtype: A subclass of :py:class:`ListServicesByLocationResponse`
        """
        raise NotImplementedError("Can't handle listServicesByLocation requests just yet, come back later.")
