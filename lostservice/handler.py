#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. currentmodule:: handler
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

Base class for all handlers and common exceptions.
"""


class Handler(object):
    """
    Base class for all types of handlers
    """
    def __init__(self):
        """
        Constructor
        """
        super(Handler, self).__init__()

    def handle_request(self, request, context):
        """
        Entry point for request handling.
        
        :param request: The request
        :type request: A subclass of :py:class:`Request`
        :param context: The context.
        :type context: :py:class:`lostservice.context.LostContext`
        :return: The response.
        :rtype: A subclass of :py:class:`Response`
        """
        raise NotImplementedError("The handle_request method must be implemented in a subclass.")
