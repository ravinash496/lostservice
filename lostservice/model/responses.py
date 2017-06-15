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
    def __init__(self, displayname=None, serviceurn=None, routeuri=None, servicenum=None, path=None, locationused=None, lastupdate=None, source=None, sourceid=None, expires=None, value_or_reference=None, non_lost_data=None, profile=None):

        """
 
        """
        super(FindServiceResponse, self).__init__()
        self._displayname = displayname
        self._serviceurn = serviceurn
        self._routeuri = routeuri
        self._servicenum = servicenum
        self._path = path
        self._locationused = locationused
        self._lastupdate = lastupdate
        self._source = source
        self._sourceid = sourceid
        self._expires = expires
        self._value_or_reference = value_or_reference
        self._profile = profile
        self._non_lost_data = non_lost_data

    @property
    def displayname(self):
        """
        The value of the displayname field.

        :rtype: string
        """
        return self._displayname

    @displayname.setter
    def displayname(self, value):
        self._displayname = value

    @property
    def serviceurn(self):
        """
        The value of the serviceurn field.

        :rtype: string
        """
        return self._serviceurn

    @serviceurn.setter
    def serviceurn(self, value):
        self._serviceurn = value

    @property
    def routeuri(self):
        """
        The value of the routeuri field.

        :rtype: string
        """
        return self._routeuri

    @routeuri.setter
    def routeuri(self, value):
        self._routeuri = value

    @property
    def servicenum(self):
        """
        The value of the servicenum field.

        :rtype: string
        """
        return self._servicenum

    @servicenum.setter
    def servicenum(self, value):
        self._servicenum = value

    @property
    def path(self):
        """
        The mapping resolution path.

        :rtype: A list of ``str``
        """
        return self._path

    @path.setter
    def path(self, value):
        self._path = value

    @property
    def locationused(self):
        """
        The location used in the request (Optional).
        Get this from the request location's id.
        This is helpful for the client so it knows which location it passed in acutally created the result.

        :rtype: A GUID
        """
        return self._locationused

    @locationused.setter
    def locationused(self, value):
        self._locationused = value

    @property
    def lastupdate(self):
        """
        The value of the lastupdate field.
        attribute describes when a specific instance of mapping was last changed.
        
        :rtype: string
        """
        return self._lastupdate

    @lastupdate.setter
    def lastupdate(self, value):
        self._lastupdate = value

    @property
    def source(self):
        """
        The value of the source field.
        The ’source’ attribute contains a LoST application unique string
        identifying the authoritative generator of the mapping
        :rtype: string
        """
        return self._source

    @source.setter
    def source(self, value):
        self._source = value

    @property
    def sourceid(self):
        """
        The value of the sourceid field.
        The ’sourceid’ attribute contains the value of the gcunqid field or is generated GUID
        identifying the authoritative generator of the mapping
        :rtype: string
        """
        return self._sourceid

    @sourceid.setter
    def sourceid(self, value):
        self._sourceid = value

    @property
    def expires(self):
        """
        The expiration value, a string that is either 'NO-CACHE', 'NO-EXPIRATION', or a datetime string
        :rtype: string
        """
        return self._expires

    @expires.setter
    def expires(self, value):
        self._expires = value

    @property
    def value_or_reference(self):
        """
        It is ultimately up to the server to decide which type to return - Value or Reference.
        :rtype: string
        """
        return self._value_or_reference

    @value_or_reference.setter
    def value_or_reference(self, value):
        self._value_or_reference = value

    @property
    def non_lost_data(self):
        """

        :rtype: string
        """
        return self._non_lost_data

    @non_lost_data.setter
    def non_lost_data(self, value):
        self._non_lost_data = value

    @property
    def profile(self):
        """

        :rtype: string
        """
        return self._profile

    @profile.setter
    def profile(self, value):
        self._profile = value


class ListServicesResponse(Response):
    """
    listServices response class.

    :param services: A list of services.
    :type services: A list of ``str``
    :param path: The mapping resolution path.
    :type path: A list of ``str``
    """
    def __init__(self, services=None, path=None):
        super(ListServicesResponse, self).__init__()
        self._services = services
        self._path = path
    
    @property
    def services(self):
        """
        The list of supported services.

        :rtype: A list of ``str``
        """
        return self._services
    
    @services.setter
    def services(self, value):
        self._services = value
    
    @property
    def path(self):
        """
        The mapping resolution path.

        :rtype: A list of ``str``
        """
        return self._path
    
    @path.setter
    def path(self, value):
        self._path = value


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
