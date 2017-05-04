#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
    def __init__(self, location=None, service=None):
        """
        :param content: 
        """
        super(FindServiceRequest, self).__init__()
        self._location = location
        self._service = service

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        self._location = value

    @property
    def service(self):
        return self._service

    @service.setter
    def service(self, value):
        self._service = value


class ListServicesRequest(Request):
    """
    listServices request class.
    """
    def __init__(self):
        super(ListServicesRequest, self).__init__()


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
    def __init(self):
        super(GetServiceBoundaryRequest, self).__init__()














