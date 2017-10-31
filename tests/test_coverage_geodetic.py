#!/usr/bin/env python
# -*- coding: utf-8 -*-


from osgeo import ogr
from shapely.geometry import Point
import unittest
from unittest.mock import patch
from unittest.mock import MagicMock, call
import lostservice.coverage.base as cov_base
import lostservice.coverage.geodetic as cov_geodetic
import lostservice.model.geodetic as mod_geodetic
import lostservice.exception as lost_exp


class GeodeticCoverageResolverTest(unittest.TestCase):

    @patch('lostservice.coverage.base.CoverageConfigWrapper')
    @patch('lostservice.model.geodetic.Point')
    def test_build_coverage_query(self, mock_config: cov_base.CoverageConfigWrapper, mock_point: mod_geodetic.Point):

        test_geom = Point(2.2, 1.1)

        mock_point.to_ogr_geometry = MagicMock()
        mock_point.to_ogr_geometry.return_value = ogr.CreateGeometryFromWkt(test_geom.wkt)

        mock_config.geodetic_coverage_table = MagicMock()
        mock_config.geodetic_coverage_table.return_value = 'the_table'

        expected = (
            """
            select depth, serviceurn, lostserver, ST_Area(ST_Intersection(ST_GeomFromText('{0}', 4326), wkb_geometry))
            from {1} 
            where ST_Intersects(ST_GeomFromText('{0}', 4326), wkb_geometry)
            order by depth desc, st_area desc
            """.format(test_geom.wkt, 'the_table')
        )

        target: cov_geodetic.GeodeticCoverageResolver = cov_geodetic.GeodeticCoverageResolver(mock_config, None)

        actual = target.build_coverage_query(mock_point)
        self.assertIsNotNone(actual)
        self.assertEqual(expected, actual)
        mock_config.geodetic_coverage_table.assert_called_once()

    @patch('lostservice.coverage.base.CoverageConfigWrapper')
    def test_build_response_with_result(self, mock_config: cov_base.CoverageConfigWrapper):
        input_matches = [
            {'depth': 1, 'serviceurn': 'urn:nena:service:sos', 'lostserver': 'one', 'area': 2.0},
            {'depth': 1, 'serviceurn': 'urn:nena:service:sos', 'lostserver': 'two', 'area': 1.5},
            {'depth': 1, 'serviceurn': 'urn:nena:service:sos', 'lostserver': 'three', 'area': 1.0},
            {'depth': 1, 'serviceurn': 'urn:nena:service:sos', 'lostserver': 'four', 'area': 0.5}
        ]

        target: cov_geodetic.GeodeticCoverageResolver = cov_geodetic.GeodeticCoverageResolver(mock_config, None)

        actual = target.build_response(input_matches)
        self.assertEqual('one', actual)

    @patch('lostservice.coverage.base.CoverageConfigWrapper')
    def test_build_response_without_result_return_parent(self, mock_config: cov_base.CoverageConfigWrapper):
        input_matches = []

        mock_config.parent_ecrf = MagicMock()
        mock_config.parent_ecrf.return_value = 'some.parent.ecrf'

        target: cov_geodetic.GeodeticCoverageResolver = cov_geodetic.GeodeticCoverageResolver(mock_config, None)

        actual = target.build_response(input_matches)
        self.assertEqual('some.parent.ecrf', actual)
        mock_config.parent_ecrf.assert_called_once()

    @patch('lostservice.coverage.base.CoverageConfigWrapper')
    def test_build_response_without_result_no_parent(self, mock_config: cov_base.CoverageConfigWrapper):
        input_matches = []

        mock_config.parent_ecrf = MagicMock()
        mock_config.parent_ecrf.return_value = None

        target: cov_geodetic.GeodeticCoverageResolver = cov_geodetic.GeodeticCoverageResolver(mock_config, None)

        with self.assertRaises(lost_exp.NotFoundException):
            actual = target.build_response(input_matches)

        mock_config.parent_ecrf.assert_called_once()


if __name__ == '__main__':
    unittest.main()