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
    def __init__(self, location=None, service=None, serviceBoundary=None, path=None, nonlostdata=None):
        """
        Constructor


        """
        super(FindServiceRequest, self).__init__()
        self._location = location
        self._service = service
        self._serviceBoundary = serviceBoundary
        self._path = path if path is not None else []
        self._nonlostdata = nonlostdata if nonlostdata is not None else []

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

    @property
    def path(self):
        """
        The path type

        :rtype: ``str``
        """
        return self._path

    @path.setter
    def path(self, value):
        self._path = value

    @property
    def nonlostdata(self):
        """
        The nonlostdata type

        :rtype: ``str``
        """
        return self._nonlostdata

    @nonlostdata.setter
    def nonlostdata(self, value):
        self._nonlostdata = value


class ListServicesRequest(Request):
    """
    listServices request class.
    """
    def __init__(self, service=None, path=None, nonlostdata=None):
        """
        Constructor

        :param service: An options base service urn.
        :type service: ``str``
        """
        super(ListServicesRequest, self).__init__()
        self._service = service
        self._path = path if path is not None else[]
        self._nonlostdata = nonlostdata if nonlostdata is not None else []

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

    @property
    def path(self):
        """
        The path type

        :rtype: ``str``
        """
        return self._path

    @path.setter
    def path(self, value):
        self._path = value

    @property
    def nonlostdata(self):
        """
        The nonlostdata type

        :rtype: ``str``
        """
        return self._nonlostdata

    @nonlostdata.setter
    def nonlostdata(self, value):
        self._nonlostdata = value


class ListServicesByLocationRequest(Request):
    """
    listServicesByLocation request class.
    """
    def __init__(self, service=None, location=None, path=None, nonlostdata=None, location_id=None):
        super(ListServicesByLocationRequest, self).__init__()
        self._service = service
        self._location = location
        self._path = path if path is not None else[]
        self._nonlostdata = nonlostdata if nonlostdata is not None else []
        self._location_id = location_id

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

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        self._location = value

    @property
    def path(self):
        """
        The path type

        :rtype: ``str``
        """
        return self._path

    @path.setter
    def path(self, value):
        self._path = value

    @property
    def nonlostdata(self):
        """
        The nonlostdata type

        :rtype: ``str``
        """
        return self._nonlostdata

    @nonlostdata.setter
    def nonlostdata(self, value):
        self._nonlostdata = value

    @property
    def location_id(self):
        """
        The location_id type

        :rtype: ``str``
        """
        return self._location_id

    @location_id.setter
    def location_id(self, value):
        self._location_id = value


class GetServiceBoundaryRequest(Request):
    """
    getServiceBoundary request class.
    """
    def __init__(self, key=None, nonlostdata=None):
        """
        Constructor

        """
        super(GetServiceBoundaryRequest, self).__init__()
        self._key = key
        self._nonlostdata = nonlostdata if nonlostdata is not None else []

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

    @property
    def nonlostdata(self):
        """
        The nonlostdata type

        :rtype: ``str``
        """
        return self._nonlostdata

    @nonlostdata.setter
    def nonlostdata(self, value):
        self._nonlostdata = value












