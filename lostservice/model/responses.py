#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: lostservice.model.responses
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

Models for different types of responses.
"""


class Response(object):
    """
    A base class for all response objects.
    """
    def __init__(self):
        """
        Base constructor for all response types.
        """
        super(Response, self).__init__()


class FindServiceResponse(Response):
    """
    findService response class.
    """
    def __init__(self):
        """
 
        """
        super(FindServiceResponse, self).__init__()


class ListServicesResponse(Response):
    """
    listServices response class.
    """
    def __init__(self):
        super(ListServicesResponse, self).__init__()


class ListServicesByLocationResponse(Response):
    """
    listServicesByLocation response class.
    """
    def __init__(self):
        super(ListServicesByLocationResponse, self).__init__()


class GetServiceBoundaryResponse(Response):
    """
    getServiceBoundary response class.
    """
    def __init(self):
        super(GetServiceBoundaryResponse, self).__init__()
