#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: lostservice.model.location
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

Models for different types of locations.
"""

from enum import Enum


class LocationType(Enum):
    """
    The supported location types.
    """
    CIVIC = 0       #: A civic address.
    GEODETIC2D = 1  #: A geodetic-2d geometry


class Location(object):
    """
    A class to encapsulate request location elements.
    """
    def __init__(self, id=None, profile=None, location=None):
        """
        Constructor for Location objects.    
        
        :param id: The location id.
        :type id: ``str``
        :param profile: The type of location, civic or geodetic-2d
        :type profile: ``str``
        """
        super(Location, self).__init__()
        self._id = id
        self._profile = profile
        self._location = location

    @property
    def id(self):
        """
        The location used in the request (Optional).
        Get this from the request location's id.
        This is helpful for the client so it knows which location it passed in acutally created the result.
        :rtype: ``str``
        """
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def profile(self):
        """
        The location profile.
        
        :rtype: ``str``
        """
        return self._profile

    @profile.setter
    def profile(self, value):
        self._profile = value

    @property
    def location_type(self):
        """
        The location type.
        
        :rtype: :py:class:`LocationType` 
        """
        return LocationType.CIVIC if "civic" == self._profile else LocationType.GEODETIC2D

    @property
    def location(self):
        """
        The location.
        
        :rtype: One of ``CivicAddress`` or a subclass of ``Geodedeic2D``
        """
        return self._location

    @location.setter
    def location(self, value):
        self._location = value


class CivicAddress(object):
    """
    A class to represent civic addresses according to the revised PIDF-LO specification.
    """

    def __init__(self, country=None, a1=None, a2=None, a3=None, a4=None,
                 a5=None, a6=None, prm=None, prd=None, rd=None, sts=None,
                 pod=None, pom=None, rdsec=None, rdbr=None, rdsubr=None,
                 hno=None, hns=None, lmk=None, loc=None, flr=None, nam=None,
                 pc=None, bld=None, unit=None, room=None, seat=None, plc=None,
                 pcn=None, pobox=None, addcode=None, stp=None, stps=None
                 ):
        super(CivicAddress, self).__init__()
        self._country = country
        self._a1 = a1
        self._a2 = a2
        self._a3 = a3
        self._a4 = a4
        self._a5 = a5
        self._a6 = a6
        self._prm = prm
        self._prd = prd
        self._rd = rd
        self._sts = sts
        self._pod = pod
        self._pom = pom
        self._rdsec = rdsec
        self._rdbr = rdbr
        self._rdsubr = rdsubr
        self._hno = hno
        self._hns = hns
        self._lmk = lmk
        self._loc = loc
        self._flr = flr
        self._nam = nam
        self._pc = pc
        self._bld = bld
        self._unit = unit
        self._room = room
        self._seat = seat
        self._plc = plc
        self._pcn = pcn
        self._pobox = pobox
        self._addcode = addcode
        self._stp = stp
        self._stps = stps

    @property
    def country(self):
        """
        The two-letter country code as described in ISO 3166.

        :rtype: ``str``
        """
        return self._country

    @country.setter
    def country(self, value):
        self._country = value

    @property
    def a1(self):
        """
        The state, region, province, or prefecture.

        :rtype: ``str`` 
        """
        return self._a1

    @a1.setter
    def a1(self, value):
        self._a1 = value

    @property
    def a2(self):
        """
        The county, parish, etc.

        :rtype: ``str`` 
        """
        return self._a2

    @a2.setter
    def a2(self, value):
        self._a2 = value

    @property
    def a3(self):
        """
        The city, township, etc.

        :rtype: ``str`` 
        """
        return self._a3

    @a3.setter
    def a3(self, value):
        self._a3 = value

    @property
    def a4(self):
        """
        The city division, borough, city district, ward, etc.

        :rtype: ``str`` 
        """
        return self._a4

    @a4.setter
    def a4(self, value):
        self._a4 = value

    @property
    def a5(self):
        """
        The neighborhood or block.

        :rtype: ``str`` 
        """
        return self._a5

    @a5.setter
    def a5(self, value):
        self._a5 = value

    @property
    def a6(self):
        """
        The street.

        :rtype: ``str`` 
        """
        return self._a6

    @a6.setter
    def a6(self, value):
        self._a6 = value

    @property
    def prm(self):
        """
        Road pre-modifier.

        :rtype: ``str`` 
        """
        return self._prm

    @prm.setter
    def prm(self, value):
        self._prm = value

    @property
    def prd(self):
        """
        The leading street direction (e.g. N, NW)

        :rtype: ``str`` 
        """
        return self._prd

    @prd.setter
    def prd(self, value):
        self._prd = value

    @property
    def rd(self):
        """
        Primary road or street.

        :rtype: ``str`` 
        """
        return self._rd

    @rd.setter
    def rd(self, value):
        self._rd = value

    @property
    def sts(self):
        """
        The street suffix (e.g. Avenue, Street).

        :rtype: ``str`` 
        """
        return self._sts

    @sts.setter
    def sts(self, value):
        self._sts = value

    @property
    def pod(self):
        """
        The trailing street suffix (e.g. S, SW)

        :rtype: ``str`` 
        """
        return self._pod

    @pod.setter
    def pod(self, value):
        self._pod = value

    @property
    def pom(self):
        """
        Road post-modifier.

        :rtype: ``str`` 
        """
        return self._pom

    @pom.setter
    def pom(self, value):
        self._pom = value

    @property
    def rdsec(self):
        """
        Road section.

        :rtype: ``str`` 
        """
        return self._rdsec

    @rdsec.setter
    def rdsec(self, value):
        self._rdsec = value

    @property
    def rdbr(self):
        """
        Road branch.

        :rtype: ``str`` 
        """
        return self._rdbr

    @rdbr.setter
    def rdbr(self, value):
        self._rdbr = value

    @property
    def rdsubr(self):
        """
        Road sub-branch.

        :rtype: ``str`` 
        """
        return self._rdsubr

    @rdsubr.setter
    def rdsubr(self, value):
        self._rdsubr = value

    @property
    def hno(self):
        """
        The house number, numeric part only.

        :rtype: ``str`` 
        """
        return self._hno

    @hno.setter
    def hno(self, value):
        self._hno = value

    @property
    def hns(self):
        """
        The house number suffix (e.g. A, 1/2)

        :rtype: ``str`` 
        """
        return self._hns

    @hns.setter
    def hns(self, value):
        self._hns = value

    @property
    def lmk(self):
        """
        The landmark or vanity address.

        :rtype: ``str`` 
        """
        return self._lmk

    @lmk.setter
    def lmk(self, value):
        self._lmk = value

    @property
    def loc(self):
        """
        Additional location information (e.g. Room 543)

        :rtype: ``str`` 
        """
        return self._loc

    @loc.setter
    def loc(self, value):
        self._loc = value

    @property
    def flr(self):
        """
        The floor.

        :rtype: ``str`` 
        """
        return self._flr

    @flr.setter
    def flr(self, value):
        self._flr = value

    @property
    def nam(self):
        """
        Name (residence, business or office occupant).

        :rtype: ``str`` 
        """
        return self._nam

    @nam.setter
    def nam(self, value):
        self._nam = value

    @property
    def pc(self):
        """
        The postal code.

        :rtype: ``str`` 
        """
        return self._pc

    @pc.setter
    def pc(self, value):
        self._pc = value

    @property
    def bld(self):
        """
        The building.

        :rtype: ``str`` 
        """
        return self._bld

    @bld.setter
    def bld(self, value):
        self._bld = value

    @property
    def unit(self):
        """
        Unit (apartment, suite)

        :rtype: ``str`` 
        """
        return self._unit

    @unit.setter
    def unit(self, value):
        self._unit = value

    @property
    def room(self):
        """
        Room number.

        :rtype: ``str`` 
        """
        return self._room

    @room.setter
    def room(self, value):
        self._room = value

    @property
    def seat(self):
        """
        Seat (e.g. desk, cubicle, workstation).

        :rtype: ``str`` 
        """
        return self._seat

    @seat.setter
    def seat(self, value):
        self._seat = value

    @property
    def plc(self):
        """
        Place type (e.g. office).

        :rtype: ``str`` 
        """
        return self._plc

    @plc.setter
    def plc(self, value):
        self._plc = value

    @property
    def pcn(self):
        """
        Postal community name.

        :rtype: ``str`` 
        """
        return self._pcn

    @pcn.setter
    def pcn(self, value):
        self._pcn = value

    @property
    def pobox(self):
        """
        Post office box.

        :rtype: ``str`` 
        """
        return self._pobox

    @pobox.setter
    def pobox(self, value):
        self._pobox = value

    @property
    def addcode(self):
        """
        Additional code.

        :rtype: ``str`` 
        """
        return self._addcode

    @addcode.setter
    def addcode(self, value):
        self._addcode = value

    @property
    def stp(self):
        """
        The street prefix.

        :rtype: ``str`` 
        """
        return self._stp

    @stp.setter
    def stp(self, value):
        self._stp = value

    @property
    def stps(self):
        """
        The street name pre type separator.

        :rtype: ``str`` 
        """
        return self._stps

    @stps.setter
    def stps(self, value):
        self._stps = value


class Geodetic2D(object):
    """
    Base class for all geodetic 2D geometries.
    """

    def __init__(self, spatial_ref=None):
        """
        Base constructor for all geodetic 2D geometries.

        :param spatial_ref: The spatial reference identifier for the given geometry.
        """
        super(Geodetic2D, self).__init__()
        self._spatial_ref = spatial_ref

    @property
    def spatial_ref(self):
        """
        The spatial reference identifier.

        :type: ``str``
        """
        return self._spatial_ref

    @spatial_ref.setter
    def spatial_ref(self, value):
        self._spatial_ref = value


class Point(Geodetic2D):
    """
    A class for representing Point geometries.
    """

    def __init__(self, spatial_ref=None, lat=None, lon=None):
        """
        Constructor for Point geometries.

        :param spatial_ref: The spatial reference identifier for the given geometry.
        :type spatial_ref: ``str``
        :param lat: Latitude
        :type lat: ``float``
        :param lon: Longitude
        :type lon: ``float``
        """
        super(Point, self).__init__(spatial_ref)
        self._lat = lat
        self._lon = lon

    @property
    def latitude(self):
        """
        The latitude.

        :rtype: ``float`` 
        """
        return self._lat

    @latitude.setter
    def latitude(self, value):
        self._lat = value

    @property
    def longitude(self):
        """
        The longitude.

        :rtype: ``float`` 
        """
        return self._lon

    @longitude.setter
    def longitude(self, value):
        self._lon = value


class Circle(Geodetic2D):
    """
    A class for representing Circle geometries.
    """

    def __init__(self, spatial_ref=None, lat=None, lon=None, radius=None, uom=None):
        """
        Constructor for Circle geometries.

        :param spatial_ref: The spatial reference URN.
        :type spatial_ref: ``str``
        :param lat: Latitude
        :type lat: ``float``
        :param lon: Longitude
        :type lon: ``float``
        :param radius: Radius of the circle
        :type radius: ``float``
        :param uom: Unit of measure identifier for the radius.
        :type uom: ``str``
        """
        super(Circle, self).__init__(spatial_ref)
        self._lat = lat
        self._lon = lon
        self._radius = radius
        self._uom = uom

    @property
    def latitude(self):
        """
        The latitude.

        :rtype: ``float`` 
        """
        return self._lat

    @latitude.setter
    def latitude(self, value):
        self._lat = value

    @property
    def longitude(self):
        """
        The longitude.

        :rtype: ``float`` 
        """
        return self._lon

    @longitude.setter
    def longitude(self, value):
        self._lon = value

    @property
    def radius(self):
        """
        The radius.

        :rtype: ``float`` 
        """
        return self._radius

    @radius.setter
    def radius(self, value):
        self._radius = value

    @property
    def uom(self):
        """
        The unit of measure identifier.

        :rtype: ``str`` 
        """
        return self._uom

    @uom.setter
    def uom(self, value):
        self._uom = value


class Ellipse(Geodetic2D):
    """
    A class for representing Ellipse geometries.
    """

    def __init__(self, spatial_ref=None, lat=None, lon=None,
                 majorAxis=None, majorAxisuom=None,
                 minorAxis=None, minorAxisuom=None,
                 orinetation=None, orinetationuom=None  ):
        """
        Constructor for Ellipse geometries.

        :param spatial_ref: The spatial reference URN.
        :type spatial_ref: ``str``
        :param lat: Latitude
        :type lat: ``float``
        :param lon: Longitude
        :type lon: ``float``
        :param majorAxis: majorAxis of the Ellipse
        :type majorAxis: ``float``
        :param majorAxisuom: Unit of measure identifier for the majorAxis.
        :type majorAxisuom: ``str``
        :param minorAxis: minorAxis of the Ellipse
        :type minorAxis: ``float``
        :param minorAxisuom: Unit of measure identifier for the minorAxis.
        :type minorAxisuom: ``str``
        :param orinetation: orinetation of the Ellipse
        :type orinetation: ``float``
        :param orinetationuom: Unit of measure identifier for the orinetation.
        :type orinetationuom: ``str``
        """
        super(Ellipse, self).__init__(spatial_ref)
        self._lat = lat
        self._lon = lon
        self._majorAxis = majorAxis
        self._majorAxisuom = majorAxisuom
        self._minorAxis = minorAxis
        self._minorAxisuom = minorAxisuom
        self._orinetation = orinetation
        self._orinetationuom = orinetationuom

    @property
    def latitude(self):
        """
        The latitude.

        :rtype: ``float``
        """
        return self._lat

    @latitude.setter
    def latitude(self, value):
        self._lat = value

    @property
    def longitude(self):
        """
        The longitude.

        :rtype: ``float``
        """
        return self._lon

    @longitude.setter
    def longitude(self, value):
        self._lon = value

    @property
    def majorAxis(self):
        """
        The _majorAxis.

        :rtype: ``float``
        """
        return self.__majorAxis

    @majorAxis.setter
    def majorAxis(self, value):
        self.__majorAxis = value

    @property
    def majorAxisuom(self):
        """
        The unit of measure identifier.

        :rtype: ``str``
        """
        return self.__majorAxisuom

    @majorAxisuom.setter
    def majorAxisuom(self, value):
        self._majorAxisuom = value

    @property
    def minorAxis(self):
        """
        The minorAxis.

        :rtype: ``float``
        """
        return self._minorAxis

    @minorAxis.setter
    def minorAxis(self, value):
        self._minorAxis = value

    @property
    def minorAxisuom(self):
        """
        The unit of measure identifier.

        :rtype: ``str``
        """
        return self._minorAxisuom

    @minorAxisuom.setter
    def minorAxisuom(self, value):
        self._minorAxisuom = value

    @property
    def orinetation(self):
        """
        The orinetation.

        :rtype: ``float``
        """
        return self._orinetation

    @orinetation.setter
    def orinetation(self, value):
        self._orinetation = value

    @property
    def orinetationuom(self):
        """
        The unit of measure identifier.

        :rtype: ``str``
        """
        return self._orinetationuom

    @orinetationuom.setter
    def orinetationuom(self, value):
        self._orinetationuom = value