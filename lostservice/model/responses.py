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
    def __init__(self, response_mapping_list = []):

        """
 
        """
        super(FindServiceResponse, self).__init__()


    @property
    def response_mapping_list(self):
        """
        The mappings and values for the response.

        :rtype: dict
        """
        return self._response_mapping_list

    @response_mapping_list.setter
    def response_mapping_list(self, value):
        self._response_mapping_list = value


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
