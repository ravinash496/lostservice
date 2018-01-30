#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: lostservice.model.civic
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

Model(s) for civic location.
"""

from civvy.db.postgis.locating.streets import PgStreetsAggregateLocatorStrategy
from civvy.db.postgis.locating.points import PgPointsAggregateLocatorStrategy
from civvy.locating import CivicAddress, CivicAddressSourceMapCollection, Locator
from civvy.db.postgis.query import PgQueryExecutor


class CivicAddress(object):
    """
    A class to represent civic addresses according to the revised PIDF-LO specification.
    """

    def __init__(self, country=None, a1=None, a2=None, a3=None, a4=None,
                 a5=None, a6=None, prm=None, prd=None, rd=None, sts=None,
                 pod=None, pom=None, rdsec=None, rdbr=None, rdsubr=None,
                 hno=None, hns=None, lmk=None, loc=None, flr=None, nam=None,
                 pc=None, bld=None, unit=None, room=None, seat=None, plc=None,
                 pcn=None, pobox=None, addcode=None, stp=None, stps=None,
                 hnp=None, lmpk=None, mp=None):
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
        self._hnp = hnp
        self._lmpk = lmpk
        self._mp = mp

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

    @property
    def hnp(self):
        """
        The address number prefix.

        :rtype: ``str``
        """
        return self._hnp

    @hnp.setter
    def hnp(self, value):
        self._hnp = value

    @property
    def lmpk(self):
        """
        The landmark name part.

        :rtype: ``str``
        """
        return self._lmpk

    @lmpk.setter
    def lmpk(self, value):
        self._lmpk = value

    @property
    def mp(self):
        """
        The milepost.

        :rtype: ``str``
        """
        return self._mp

    @mp.setter
    def mp(self, value):
        self._mp = value

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]

    def __repr__(self):
        return repr(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __delitem__(self, key):
        del self.__dict__[key]

    def clear(self):
        return self.__dict__.clear()

    def copy(self):
        return self.__dict__.copy()

    def has_key(self, k):
        return k in self.__dict__

    def update(self, *args, **kwargs):
        return self.__dict__.update(*args, **kwargs)

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

    def items(self):
        return self.__dict__.items()

    def pop(self, *args):
        return self.__dict__.pop(*args)

    def __contains__(self, item):
        return item in self.__dict__

    def __iter__(self):
        return iter(self.__dict__)

    def __unicode__(self):
        return unicode(repr(self.__dict__))
