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


class ResponseMapping(object):
    """
    A container for a single response mapping.
    """
    # <mapping expires="NO-CACHE" lastUpdated="2017-05-16 09:00:22+00:00" source="authoritative.example" sourceId="{5D9C9865-FE50-4CEB-917D-CBBD56DB462F}">
    #     <displayName xml:lang="en">Lincoln Ambulance</displayName>
    #     <service>urn:nena:service:sos.EMS</service>
    #     <serviceBoundaryReference source="authoritative.example" key="{5D9C9865-FE50-4CEB-917D-CBBD56DB462F}"/>
    #     <uri>SIP:+2075555883@lincolnambulance.ngesi.maine.gov</uri>
    #     <serviceNumber>2075555883</serviceNumber>
    # </mapping>

    def __init__(self,
                 source=None,
                 source_id=None,
                 last_updated=None,
                 expires=None,
                 display_name=None,
                 service_urn=None,
                 service_number=None,
                 route_uri=None,
                 boundary_value=None):
        """

        :param source: the URI of the service that found the mapping (source_uri from config).
        :param source_id: the unique id of the mapping (srcunqid).
        :param last_updated: time of last update for the mapping (updatedate).
        :param expires: policy based expiration.
        :param display_name: the human readable name (from displayname).
        :param service_urn: the service URN of the request (see section 5.4 of RFC 5222 for special handling).
        :param service_number: the phone number (servicenum).
        :param route_uri: the service uri (from routeuri).
        :param boundary_value: full boundary information when asked for by value
        """
        super(ResponseMapping, self).__init__()
        self._source = source
        self._source_id = source_id
        self._last_updated = last_updated
        self._expires = expires
        self._display_name = display_name
        self._service = service_urn
        self._service_number = service_number
        self._route_uri = route_uri
        self._boundary_value = boundary_value

    @property
    def source(self):
        """
        The source of the mapping.

        :return: ``str``
        """
        return self._source

    @source.setter
    def source(self, value):
        self._source = value

    @property
    def source_id(self):
        """
        The id of the mapping from the associated source.

        :return: ``str``
        """
        return self._source_id

    @source_id.setter
    def source_id(self, value):
        self._source_id = value

    @property
    def last_updated(self):
        """
        The last update date of the mapping.

        :return: ``str``
        """
        return self._last_updated

    @last_updated.setter
    def last_updated(self, value):
        self._last_updated = value

    @property
    def expires(self):
        """
        The expiration of the mapping.

        :return: ``str``
        """
        return self._expires

    @expires.setter
    def expires(self, value):
        self._expires = value

    @property
    def display_name(self):
        """
        The display name for the mapping.

        :return: ``str``
        """
        return self._display_name

    @display_name.setter
    def display_name(self, value):
        self._display_name = value

    @property
    def service(self):
        """
        The service URN for the mapping (usually same as the URN in the request)

        :return: ``str``
        """
        return self._service

    @service.setter
    def service(self, value):
        self._service = value

    @property
    def service_number(self):
        """
        The service (phone) number for the mapping.

        :return: ``str``
        """
        return self._service_number

    @service_number.setter
    def service_number(self, value):
        self._service_number = value

    @property
    def route_uri(self):
        """
        The route URI for the mapping (from routeuri).

        :return: ``str``
        """
        return self._route_uri

    @route_uri.setter
    def route_uri(self, value):
        self._route_uri = value

    @property
    def boundary_value(self):
        """
        The service boundary GML.

        :return: ``str`` or :py:class:`_ElementTree`
        """
        return self._boundary_value

    @boundary_value.setter
    def boundary_value(self, value):
        self._boundary_value = value


class AdditionalDataResponseMapping(object):
    """
    A container for a single Additional Data response mapping.
    """
    # <mapping expires="NO-CACHE" lastUpdated="2017-05-16 09:00:22+00:00" source="authoritative.example" sourceId="{5D9C9865-FE50-4CEB-917D-CBBD56DB462F}">
    #   <service>urn:nena:service:adddatauri</service>
    #   <adddatauri>http://pv-qps-2/testdoc609784.doc</adddatauri>
    # </mapping>
    def __init__(self,
                 source=None,
                 source_id=None,
                 last_updated=None,
                 expires=None,
                 service_urn=None,
                 adddatauri=None):
        """

        :param source: The URI of the service that is found in the mapping.(source_uri from config).
        :param source_id: The unique ID of the mapping(srcunqid).
        :param last_updated: Time of last update for the mapping(updatedate).
        :param expires: Policy based expiration.
        :param service_urn: The Service URN of the request. See section 5.4 of RCC 5222 for special handling.
        :param adddatauri: The additional data URI.
        """
        super(AdditionalDataResponseMapping, self).__init__()
        self._source = source
        self._source_id = source_id
        self._last_updated = last_updated
        self._expires = expires
        self._service = service_urn
        self._adddatauri = adddatauri

    @property
    def source(self):
        """
        The source of the mapping.

        :return: ``str``
        """
        return self._source

    @source.setter
    def source(self, value):
        self._source = value

    @property
    def source_id(self):
        """
        The id of the mapping from the associated source.

        :return: ``str``
        """
        return self._source_id

    @source_id.setter
    def source_id(self, value):
        self._source_id = value

    @property
    def last_updated(self):
        """
        The last update date of the mapping.

        :return: ``str``
        """
        return self._last_updated

    @last_updated.setter
    def last_updated(self, value):
        self._last_updated = value

    @property
    def expires(self):
        """
        The expiration of the mapping.

        :return: ``str``
        """
        return self._expires

    @expires.setter
    def expires(self, value):
        self._expires = value

    @property
    def service(self):
        """
        The service URN for the mapping (usually same as the URN in the request)

        :return: ``str``
        """
        return self._service

    @service.setter
    def service(self, value):
        self._service = value

    @property
    def adddatauri(self):
        """
        The add data uri.

        :return: ``str`` or :py:class:`_ElementTree`
        """
        return self._adddatauri

    @adddatauri.setter
    def adddatauri(self, value):
        self._adddatauri = value


class FindServiceResponse(Response):
    """
    findService response class.
    """

    def __init__(self, mappings=None, path=None, location_used=None, nonlostdata=None):
        """
        Constructor.

        :param mappings: The list of response mappings.
        :type mappings: ``list`` of :py:class:`lostservice.model.responses.ResponseMapping`
        :param path: LoST service URIs that were used in creating this response.
        :type path: ``list`` of ``str``
        :param location_used: The unique id of the location used in this query.
        :type location_used: ``str``
        """
        super(FindServiceResponse, self).__init__()
        self._mappings = mappings if mappings is not None else []
        self._path = path if path is not None else []
        self._location_used = location_used
        self._nonlostdata = nonlostdata if nonlostdata is not None else []

    @property
    def mappings(self):
        """
        The mappings and values for the response.

        :rtype: ``list`` of :py:class:`lostservice.model.responses.ResponseMapping`
        """
        return self._mappings

    @mappings.setter
    def mappings(self, value):
        self._mappings = value

    @property
    def path(self):
        """
        The list of services that participated in the response.

        :rtype: ``list`` of ``str``
        """
        return self._path

    @path.setter
    def path(self, value):
        self._path = value

    @property
    def location_used(self):
        """
        The location used in this query.

        :return: ``str``
        """
        return self._location_used

    @location_used.setter
    def location_used(self, value):
        self._location_used = value

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


class ListServicesResponse(Response):
    """
    listServices response class.

    :param services: A list of services.
    :type services: A list of ``str``
    :param path: The mapping resolution path.
    :type path: A list of ``str``
    """
    def __init__(self, services=None, path=None, nonlostdata=[]):
        super(ListServicesResponse, self).__init__()
        self._services = services
        self._path = path
        self._nonlostdata=nonlostdata
    
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


    @property
    def nonlostdata(self):
        """
        The mapping resolution path.
    
        :rtype: A list of ``str``
        """
        return self._nonlostdata

    @nonlostdata.setter
    def nonlostdata(self, value):
        self._nonlostdata = value


class ListServicesByLocationResponse(Response):
    """
    listServicesByLocation response class.
    """
    def __init__(self, services=None, path=None, nonlostdata=[], location_id=None):
        super(ListServicesByLocationResponse, self).__init__()
        self._services = services
        self._path = path
        self._nonlostdata = nonlostdata
        self._location_id = location_id

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

    @property
    def nonlostdata(self):
        """
        The mapping resolution path.

        :rtype: A list of ``str``
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


class GetServiceBoundaryResponse(Response):
    """
    getServiceBoundary response class.
    """
    def __init(self):
        super(GetServiceBoundaryResponse, self).__init__()
