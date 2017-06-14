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
    def __init__(self, config, db_wrapper):
        """
        Constructor

        :param config: The configuration
        :type config: :py:class:`lostservice.configuration.Configuration`
        :param db_wrapper: The db wrapper class instance.
        :type db_wrapper: :py:class:`lostservice.db.gisdb.GisDbInterface`
        """
        super(Handler, self).__init__()
        self._config = config
        self._db_wrapper = db_wrapper

    def handle_request(self, request, context):
        """
        Entry point for request handling.
        
        :param request: The request.
        :type request: A subclass of :py:class:`Request`
        :param context: The request context.
        :type context: ``dict``
        :return: The response.
        :rtype: A subclass of :py:class:`Response`
        """
        raise NotImplementedError("The handle_request method must be implemented in a subclass.")
