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
