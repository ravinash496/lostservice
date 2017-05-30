#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. currentmodule:: lostservice.handling.listservices
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

Handler(s) for listServices* requests
"""


from lostservice.handler import Handler


class ListServicesByLocationHandler(Handler):
    """
    Base listServicesByLocation request handler.
    """

    def __init__(self):
        """
        Constructor
        """
        super(ListServicesByLocationHandler, self).__init__()

    def handle_request(self, request, context):
        """
        Entry point for request handling.

        :param request: The request
        :type request: A subclass of :py:class:`ListServicesByLocationRequest`
        :param context: The context.
        :type context: :py:class:`lostservice.context.LostContext`
        :return: The response.
        :rtype: A subclass of :py:class:`ListServicesByLocationResponse`
        """












