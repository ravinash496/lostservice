#!/usr/bin/env python
# -*- coding: utf-8 -*-


import unittest

from lostservice.geometry import reproject_point
from lostservice.geometry import reproject_geom
from lostservice.geometry import getutmsrid
from lostservice.geometry import calculate_arc
from lostservice.geometry import generate_arcband
from lostservice.geometry import get_vertices_for_geom

class GeometryTest(unittest.TestCase):
    def test_reproject_point_3463(self):
        """
        Convert x/y in 3463 (NAD_1983_Maine_2000_Central_Zone Meters) 
        to 4326 WGS84.  Used ArcMap to verify original results.
        :return: 
        """
        x= 521164.168
        y = 377812.968
        source_srid = 3463
        target_srid = 4326

        resultx, resulty = reproject_point(x, y, source_srid, target_srid)

        # Verify value is within (-/+) .000000001
        self.assertAlmostEqual(resultx, -68.84724495254032, delta=.000000001)
        self.assertAlmostEqual(resulty, 46.899295967195435, delta=.000000001)

    def test_reproject_point_4326(self):
        """
        Convert x/y in 4326 WGS84  
        to 3463 (NAD_1983_Maine_2000_Central_Zone Meters).  Used ArcMap to verify original results.
        :return: 
        """
        x = -68.84724495254032
        y = 46.899295967195435
        source_srid = 4326
        target_srid = 3463

        resultx, resulty = reproject_point(x, y, source_srid, target_srid)

        # Verify value is within (-/+) .000000001
        self.assertAlmostEqual(resultx, 521164.1680000003, delta=.000000001)
        self.assertAlmostEqual(resulty, 377812.9680000007, delta=.000000001)

    def test_getutmsrid(self):
        """
        Convert Long/Lat to UTM Zone WGS_1984_UTM_Zone_19N 32619
        :return: 
        """

        longitude = -68.84724495254032
        latitude = 46.899295967195435

        result = getutmsrid(longitude, latitude)

        self.assertEqual(result, 32619)

if __name__ == '__main__':
    unittest.main()
