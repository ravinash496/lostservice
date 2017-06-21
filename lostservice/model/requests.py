#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: lostservice.model.requests
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

Models for different types of requests.
"""


class Request(object):
    """
    A base class for all request objects.
    """
    def __init__(self):
        """
        Base constructor for all request types.
        """
        super(Request, self).__init__()


class FindServiceRequest(Request):
    """
    findService request class.
    """
    def __init__(self, location=None, service=None, serviceBoundary=None):
        """
        Constructor


        """
        super(FindServiceRequest, self).__init__()
        self._location = location
        self._service = service
        self._serviceBoundary = serviceBoundary

    @property
    def location(self):
        """
        The location.
        
        :rtype: :py:class:`Location` 
        """
        return self._location

    @location.setter
    def location(self, value):
        self._location = value

    @property
    def service(self):
        """
        The service type.
        
        :rtype: ``str`` 
        """
        return self._service

    @service.setter
    def service(self, value):
        self._service = value

    @property
    def serviceBoundary(self):
        """
        The service bodundary type

        :rtype: ``str``
        """
        return self._serviceBoundary

    @serviceBoundary.setter
    def serviceBoundary(self, value):
        self._serviceBoundary = value



class ListServicesRequest(Request):
    """
    listServices request class.
    """
    def __init__(self, service=None):
        """
        Constructor

        :param service: An options base service urn.
        :type service: ``str``
        """
        super(ListServicesRequest, self).__init__()
        self._service = service

    @property
    def service(self):
        """
        The (optional) service type.

        :rtype: ``str``
        """
        return self._service
    
    @service.setter
    def service(self, value):
        self._service = value


class ListServicesByLocationRequest(Request):
    """
    listServicesByLocation request class.
    """
    def __init__(self):
        super(ListServicesByLocationRequest, self).__init__()


class GetServiceBoundaryRequest(Request):
    """
    getServiceBoundary request class.
    """
    def __init(self,key=None):
        super(GetServiceBoundaryRequest, self).__init__()
        self._key=key

    @property
    def key(self):
        """
        The key type.

        :rtype: ``int``
        """
        return self._key

    @key.setter
    def key(self, value):
        self._key = value














