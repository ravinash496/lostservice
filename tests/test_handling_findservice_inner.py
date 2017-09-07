#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lxml import etree
import unittest
from unittest.mock import patch
from unittest.mock import MagicMock, call
import lostservice.handling.core
import lostservice.handling.findservice
import lostservice.model.requests
import lostservice.model.responses
import lostservice.model.location


class FindServiceInnerTest(unittest.TestCase):

    @patch('lostservice.handling.findservice.FindServiceConfigWrapper')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_service_expiration_policy_nocache(self, mock_config, mock_db):
        mock_config.source_uri = MagicMock()
        mock_config.source_uri.return_value = 'foo'
        mock_config.settings_for_service = MagicMock()
        mock_config.settings_for_service.return_value = {
            'service_expire_policy': 'NoCache',
            'service_cache_timespan': '15'
        }

        mock_db.get_urn_table_mappings = MagicMock()
        mock_db.get_urn_table_mappings.return_value = {'urn1': 'service1', 'urn2': 'service2' }

        target = lostservice.handling.findservice.FindServiceInner(mock_config, mock_db)

        actual = target._get_service_expiration_policy('urn1')

        self.assertEqual(actual, 'NO-CACHE')
        mock_db.get_urn_table_mappings.assert_called_once()
        mock_config.settings_for_service.assert_called_once()
        mock_config.settings_for_service.assert_called_with('service1')

    @patch('lostservice.handling.findservice.FindServiceConfigWrapper')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_service_expiration_policy_noexpiration(self, mock_config, mock_db):
        mock_config.source_uri = MagicMock()
        mock_config.source_uri.return_value = 'foo'
        mock_config.settings_for_service = MagicMock()
        mock_config.settings_for_service.return_value = {
            'service_expire_policy': 'NoExpiration',
            'service_cache_timespan': '15'
        }

        mock_db.get_urn_table_mappings = MagicMock()
        mock_db.get_urn_table_mappings.return_value = {'urn1': 'service1', 'urn2': 'service2'}

        target = lostservice.handling.findservice.FindServiceInner(mock_config, mock_db)

        actual = target._get_service_expiration_policy('urn1')

        self.assertEqual(actual, 'NO-EXPIRATION')
        mock_db.get_urn_table_mappings.assert_called_once()
        mock_config.settings_for_service.assert_called_once()
        mock_config.settings_for_service.assert_called_with('service1')

    @patch('lostservice.handling.findservice.FindServiceConfigWrapper')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_service_expiration_policy_timespan(self, mock_config, mock_db):
        mock_config.source_uri = MagicMock()
        mock_config.source_uri.return_value = 'foo'
        mock_config.settings_for_service = MagicMock()
        mock_config.settings_for_service.return_value = {
            'service_expire_policy': 'TimeSpan',
            'service_cache_timespan': '15'
        }

        mock_db.get_urn_table_mappings = MagicMock()
        mock_db.get_urn_table_mappings.return_value = {'urn1': 'service1', 'urn2': 'service2'}

        target = lostservice.handling.findservice.FindServiceInner(mock_config, mock_db)

        actual = target._get_service_expiration_policy('urn1')

        # Just assert it's not any of the others?
        self.assertNotEqual(actual, 'NO-EXPIRATION')
        self.assertNotEqual(actual, 'NO-CACHE')
        mock_db.get_urn_table_mappings.assert_called_once()
        mock_config.settings_for_service.assert_called_once()
        mock_config.settings_for_service.assert_called_with('service1')

    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_clear_attributes(self, mock_db):
        mock_db.get_urn_table_mappings = MagicMock()
        mock_db.get_urn_table_mappings.return_value = {'urn1': 'service1', 'urn2': 'service2'}

        xml = """
                    <gml:Polygon xmlns:gml="http://www.opengis.net/gml">
                        <gml:exterior>
                            <gml:LinearRing>
                                <gml:posList srsDimension="2">
                                    44.949985629000025 -68.804763547999983 44.946540828000025 -68.80386888299995
                                </gml:posList>
                            </gml:LinearRing>
                        </gml:exterior>
                    </gml:Polygon>
            """
        root = etree.fromstring(xml)

        output = """
                    <gml:Polygon xmlns:gml="http://www.opengis.net/gml">
                        <gml:exterior>
                            <gml:LinearRing>
                                <gml:posList>
                                    44.949985629000025 -68.804763547999983 44.946540828000025 -68.80386888299995
                                </gml:posList>
                            </gml:LinearRing>
                        </gml:exterior>
                    </gml:Polygon>
            """
        expected = etree.tostring(etree.fromstring(output), pretty_print=False)

        target = lostservice.handling.findservice.FindServiceInner(None, mock_db)

        actual_xml = target._clear_attributes(root)
        actual = etree.tostring(actual_xml, pretty_print=False)

        self.assertEqual(actual, expected)

    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_apply_service_boundary_policy(self, mock_db):
        mock_db.get_urn_table_mappings = MagicMock()
        mock_db.get_urn_table_mappings.return_value = {'urn1': 'service1', 'urn2': 'service2'}

        xml = """
            <gml:MultiSurface srsName="EPSG:4326">
                <gml:surfaceMember>
                    <gml:Polygon>
                        <gml:exterior>
                            <gml:LinearRing>
                                <gml:posList srsDimension="2">
                                    44.949985629000025 -68.804763547999983 44.946540828000025 -68.80386888299995
                                </gml:posList>
                            </gml:LinearRing>
                        </gml:exterior>
                    </gml:Polygon>
                </gml:surfaceMember>
            </gml:MultiSurface>
            """

        output = """
                    <gml:Polygon srsName="EPSG:4326" xmlns:gml="http://www.opengis.net/gml">
                        <gml:exterior>
                            <gml:LinearRing>
                                <gml:posList>
                                    44.949985629000025 -68.804763547999983 44.946540828000025 -68.80386888299995
                                </gml:posList>
                            </gml:LinearRing>
                        </gml:exterior>
                    </gml:Polygon>
            """
        parsed_output = etree.tostring(etree.fromstring(output), pretty_print=False).decode("utf-8")

        input = {'gcunqid': '12345', 'ST_AsGML_1': xml}
        expected = {'gcunqid': '12345', 'ST_AsGML_1': parsed_output}

        target = lostservice.handling.findservice.FindServiceInner(None, mock_db)

        actual = target._apply_service_boundary_policy(input, True)

        self.assertEqual(len(input.keys()), 2)
        self.assertDictEqual(input, expected)
        self.assertEqual(input['ST_AsGML_1'], expected['ST_AsGML_1'])
        self.assertEqual(input['gcunqid'], expected['gcunqid'])

    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_apply_service_boundary_policy_no_value(self, mock_db):
        mock_db.get_urn_table_mappings = MagicMock()
        mock_db.get_urn_table_mappings.return_value = {'urn1': 'service1', 'urn2': 'service2'}

        input = {'gcunqid': '12345'}
        expected = {'gcunqid': '12345'}

        target = lostservice.handling.findservice.FindServiceInner(None, mock_db)

        actual = target._apply_service_boundary_policy(input, True)

        self.assertEqual(len(input.keys()), 1)
        self.assertDictEqual(input, expected)
        self.assertEqual(input['gcunqid'], expected['gcunqid'])

    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_apply_service_boundary_policy_return_shape_false(self, mock_db):
        mock_db.get_urn_table_mappings = MagicMock()
        mock_db.get_urn_table_mappings.return_value = {'urn1': 'service1', 'urn2': 'service2'}

        input = {'gcunqid': '12345', 'ST_AsGML_1': 'something'}
        expected = {'gcunqid': '12345', 'ST_AsGML_1': 'something'}

        target = lostservice.handling.findservice.FindServiceInner(None, mock_db)

        actual = target._apply_service_boundary_policy(input, False)

        self.assertEqual(len(input.keys()), 2)
        self.assertDictEqual(input, expected)
        self.assertEqual(input['ST_AsGML_1'], expected['ST_AsGML_1'])
        self.assertEqual(input['gcunqid'], expected['gcunqid'])

    @patch('lostservice.handling.findservice.FindServiceConfigWrapper')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_apply_policies(self, mock_config, mock_db):
        mock_config.source_uri = MagicMock()
        mock_config.source_uri.return_value = 'foo'
        mock_config.settings_for_service = MagicMock()
        mock_config.settings_for_service.return_value = {
            'service_expire_policy': 'NoCache',
            'service_cache_timespan': '15'
        }
        mock_db.get_urn_table_mappings = MagicMock()
        mock_db.get_urn_table_mappings.return_value = {'urn1': 'service1', 'urn2': 'service2'}

        input = [{'gcunqid': '12345', 'serviceurn': 'urn1', 'ST_AsGML_1': 'something'}]
        expected = [{'gcunqid': '12345', 'serviceurn': 'urn1', 'ST_AsGML_1': 'something', 'expiration': 'NO-CACHE'}]

        target = lostservice.handling.findservice.FindServiceInner(mock_config, mock_db)

        actual = target._apply_policies(input, False)

        mock_db.get_urn_table_mappings.assert_called_once()
        mock_config.settings_for_service.assert_called_once()
        mock_config.settings_for_service.assert_called_with('service1')
        self.assertListEqual(actual, expected)
        self.assertDictEqual(actual[0], expected[0])
        self.assertEqual(actual[0]['ST_AsGML_1'], expected[0]['ST_AsGML_1'])
        self.assertEqual(actual[0]['gcunqid'], expected[0]['gcunqid'])
        self.assertEqual(actual[0]['expiration'], 'NO-CACHE')

    @patch('lostservice.handling.findservice.FindServiceConfigWrapper')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_apply_polygon_policy_limit(self, mock_config, mock_db):
        mock_config.polygon_multiple_match_policy = MagicMock()
        mock_config.polygon_multiple_match_policy.return_value = \
            lostservice.handling.findservice.PolygonMultipleMatchPolicyEnum.ReturnLimitWarning
        mock_config.polygon_result_limit_policy = MagicMock()
        mock_config.polygon_result_limit_policy.return_value = 3

        mock_db.get_urn_table_mappings = MagicMock()
        mock_db.get_urn_table_mappings.return_value = {'urn1': 'service1', 'urn2': 'service2'}

        input = [
            {'id': 1, 'AREA_RET': 2},
            {'id': 2, 'AREA_RET': 10},
            {'id': 3, 'AREA_RET': 5},
            {'id': 4, 'AREA_RET': 5}
        ]
        expected = [
            {'id': 1, 'AREA_RET': 2, 'tooManyMappings': True},
            {'id': 2, 'AREA_RET': 10, 'tooManyMappings': True},
            {'id': 3, 'AREA_RET': 5, 'tooManyMappings': True}
        ]

        target = lostservice.handling.findservice.FindServiceInner(mock_config, mock_db)
        actual = target._apply_polygon_multiple_match_policy(input)

        self.assertListEqual(actual, expected)
        mock_config.polygon_multiple_match_policy.assert_called_once()
        mock_config.polygon_result_limit_policy.assert_called_once()

    @patch('lostservice.handling.findservice.FindServiceConfigWrapper')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_apply_addtionaldata_multiple_match_policy(self, mock_config, mock_db):
        mock_config.additionaldata_result_limit = MagicMock()
        mock_config.additionaldata_result_limit.return_value = 3

        mock_db.get_urn_table_mappings = MagicMock()
        mock_db.get_urn_table_mappings.return_value = {'urn1': 'service1', 'urn2': 'service2'}

        input = [
            {'id': 1},
            {'id': 2},
            {'id': 3},
            {'id': 4}
        ]
        expected = [
            {'id': 1, 'tooManyMappings': True},
            {'id': 2, 'tooManyMappings': True},
            {'id': 3, 'tooManyMappings': True}
        ]

        target = lostservice.handling.findservice.FindServiceInner(mock_config, mock_db)
        actual = target._apply_addtionaldata_multiple_match_policy(input)

        self.assertListEqual(actual, expected)

    @patch('lostservice.handling.findservice.FindServiceConfigWrapper')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_apply_polygon_policy_limit_only_two(self, mock_config, mock_db):
        mock_config.polygon_multiple_match_policy = MagicMock()
        mock_config.polygon_multiple_match_policy.return_value = \
            lostservice.handling.findservice.PolygonMultipleMatchPolicyEnum.ReturnLimitWarning
        mock_config.polygon_result_limit_policy = MagicMock()
        mock_config.polygon_result_limit_policy.return_value = 3

        mock_db.get_urn_table_mappings = MagicMock()
        mock_db.get_urn_table_mappings.return_value = {'urn1': 'service1', 'urn2': 'service2'}

        input = [
            {'id': 1, 'AREA_RET': 2},
            {'id': 2, 'AREA_RET': 10}
        ]
        expected = [
            {'id': 1, 'AREA_RET': 2},
            {'id': 2, 'AREA_RET': 10}
        ]

        target = lostservice.handling.findservice.FindServiceInner(mock_config, mock_db)
        actual = target._apply_polygon_multiple_match_policy(input)

        self.assertListEqual(actual, expected)
        mock_config.polygon_multiple_match_policy.assert_called_once()
        mock_config.polygon_result_limit_policy.assert_called_once()

    @patch('lostservice.handling.findservice.FindServiceConfigWrapper')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_apply_polygon_policy_first(self, mock_config, mock_db):
        mock_config.polygon_multiple_match_policy = MagicMock()
        mock_config.polygon_multiple_match_policy.return_value = \
            lostservice.handling.findservice.PolygonMultipleMatchPolicyEnum.ReturnFirst

        mock_db.get_urn_table_mappings = MagicMock()
        mock_db.get_urn_table_mappings.return_value = {'urn1': 'service1', 'urn2': 'service2'}

        input = [1, 2, 3, 4, 5, 6, 7, 8]
        expected = [1]

        target = lostservice.handling.findservice.FindServiceInner(mock_config, mock_db)
        actual = target._apply_polygon_multiple_match_policy(input)

        self.assertListEqual(actual, expected)
        mock_config.polygon_multiple_match_policy.assert_called_once()

    @patch('lostservice.handling.findservice.FindServiceConfigWrapper')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_apply_polygon_policy_area_majority(self, mock_config, mock_db):
        mock_config.polygon_multiple_match_policy = MagicMock()
        mock_config.polygon_multiple_match_policy.return_value = \
            lostservice.handling.findservice.PolygonMultipleMatchPolicyEnum.ReturnAreaMajority

        mock_db.get_urn_table_mappings = MagicMock()
        mock_db.get_urn_table_mappings.return_value = {'urn1': 'service1', 'urn2': 'service2'}

        input = [{'id': 1, 'AREA_RET': 2}, {'id': 2, 'AREA_RET': 10}, {'id': 1, 'AREA_RET': 5}]
        expected = [{'id': 2, 'AREA_RET': 10}]

        target = lostservice.handling.findservice.FindServiceInner(mock_config, mock_db)
        actual = target._apply_polygon_multiple_match_policy(input)

        self.assertListEqual(actual, expected)
        mock_config.polygon_multiple_match_policy.assert_called_once()


    @patch('lostservice.handling.findservice.FindServiceConfigWrapper')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_apply_point_policy_limit(self, mock_config, mock_db):
        mock_config.point_multiple_match_policy = MagicMock()
        mock_config.point_multiple_match_policy.return_value = \
            lostservice.handling.findservice.PointMultipleMatchPolicyEnum.ReturnLimitWarning
        mock_config.point_result_limit_policy = MagicMock()
        mock_config.point_result_limit_policy.return_value = 3

        mock_db.get_urn_table_mappings = MagicMock()
        mock_db.get_urn_table_mappings.return_value = {'urn1': 'service1', 'urn2': 'service2'}

        input = [
            {'id': 1, 'AREA_RET': 2},
            {'id': 2, 'AREA_RET': 10},
            {'id': 3, 'AREA_RET': 5},
            {'id': 4, 'AREA_RET': 5}
        ]
        expected = [
            {'id': 1, 'AREA_RET': 2, 'tooManyMappings': True},
            {'id': 2, 'AREA_RET': 10, 'tooManyMappings': True},
            {'id': 3, 'AREA_RET': 5, 'tooManyMappings': True}
        ]

        target = lostservice.handling.findservice.FindServiceInner(mock_config, mock_db)
        actual = target._apply_point_multiple_match_policy(input)

        self.assertListEqual(actual, expected)
        mock_config.point_multiple_match_policy.assert_called_once()
        mock_config.point_result_limit_policy.assert_called_once()

    @patch('lostservice.handling.findservice.FindServiceConfigWrapper')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_apply_point_policy_limit_only_two(self, mock_config, mock_db):
        mock_config.point_multiple_match_policy = MagicMock()
        mock_config.point_multiple_match_policy.return_value = \
            lostservice.handling.findservice.PointMultipleMatchPolicyEnum.ReturnLimitWarning
        mock_config.point_result_limit_policy = MagicMock()
        mock_config.point_result_limit_policy.return_value = 5

        mock_db.get_urn_table_mappings = MagicMock()
        mock_db.get_urn_table_mappings.return_value = {'urn1': 'service1', 'urn2': 'service2'}

        input = [
            {'id': 1, 'AREA_RET': 2},
            {'id': 2, 'AREA_RET': 10}
        ]
        expected = [
            {'id': 1, 'AREA_RET': 2},
            {'id': 2, 'AREA_RET': 10}
        ]

        target = lostservice.handling.findservice.FindServiceInner(mock_config, mock_db)
        actual = target._apply_point_multiple_match_policy(input)

        self.assertListEqual(actual, expected)
        mock_config.point_multiple_match_policy.assert_called_once()
        mock_config.point_result_limit_policy.assert_called_once()

    @patch('lostservice.handling.findservice.FindServiceConfigWrapper')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_apply_point_policy_first(self, mock_config, mock_db):
        mock_config.point_multiple_match_policy = MagicMock()
        mock_config.point_multiple_match_policy.return_value = \
            lostservice.handling.findservice.PointMultipleMatchPolicyEnum.ReturnFirst

        mock_db.get_urn_table_mappings = MagicMock()
        mock_db.get_urn_table_mappings.return_value = {'urn1': 'service1', 'urn2': 'service2'}

        input = [1, 2, 3, 4, 5, 6, 7, 8]
        expected = [1]

        target = lostservice.handling.findservice.FindServiceInner(mock_config, mock_db)
        actual = target._apply_point_multiple_match_policy(input)

        self.assertListEqual(actual, expected)
        mock_config.point_multiple_match_policy.assert_called_once()

    @patch('lostservice.handling.findservice.FindServiceConfigWrapper')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_apply_point_policy_exception(self, mock_config, mock_db):
        mock_config.point_multiple_match_policy = MagicMock()
        mock_config.point_multiple_match_policy.return_value = \
            lostservice.handling.findservice.PointMultipleMatchPolicyEnum.ReturnError

        mock_db.get_urn_table_mappings = MagicMock()
        mock_db.get_urn_table_mappings.return_value = {'urn1': 'service1', 'urn2': 'service2'}

        input = [{'id': 1, 'AREA_RET': 2}, {'id': 2, 'AREA_RET': 10}, {'id': 1, 'AREA_RET': 5}]

        target = lostservice.handling.findservice.FindServiceInner(mock_config, mock_db)

        with self.assertRaises(lostservice.exception.InternalErrorException):
            actual = target._apply_point_multiple_match_policy(input)

    @patch('lostservice.handling.findservice.FindServiceConfigWrapper')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_find_service_for_point(self, mock_config, mock_db):

        test_data = [{'id': 1, 'AREA_RET': 2}, {'id': 2, 'AREA_RET': 10}, {'id': 1, 'AREA_RET': 5}]

        mock_db.get_urn_table_mappings = MagicMock()
        mock_db.get_urn_table_mappings.return_value = {'urn1': 'service1', 'urn2': 'service2'}
        mock_db.get_containing_boundary_for_point = MagicMock()
        mock_db.get_containing_boundary_for_point.return_value = test_data

        target = lostservice.handling.findservice.FindServiceInner(mock_config, mock_db)
        target._apply_point_multiple_match_policy = MagicMock()
        target._apply_point_multiple_match_policy.return_value = test_data
        target._apply_polygon_multiple_match_policy = MagicMock()
        target._apply_policies = MagicMock()
        target._apply_policies.return_value = test_data

        actual = target.find_service_for_point('urn1', 0.0, 1.1, 'something', False)
        buffer_dist = mock_config.additional_data_buffer()

        self.assertListEqual(actual, test_data)
        mock_db.get_containing_boundary_for_point.assert_called_with(0.0, 1.1, 'something', 'service1',
                                                                     add_data_requested=False,
                                                                     buffer_distance = buffer_dist)
        mock_db.get_containing_boundary_for_point.assert_called_once()
        target._apply_point_multiple_match_policy.assert_called_with(test_data)
        target._apply_point_multiple_match_policy.assert_called_once()
        target._apply_polygon_multiple_match_policy.assert_not_called()
        target._apply_policies.assert_called_with(test_data, False)
        target._apply_policies.assert_called_once()

    @patch('lostservice.handling.findservice.FindServiceConfigWrapper')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_find_service_for_point_expanded(self, mock_config, mock_db):
        test_data = [{'id': 1, 'AREA_RET': 2}, {'id': 2, 'AREA_RET': 10}, {'id': 1, 'AREA_RET': 5}]

        # Set up mock_db to return nothing from point search but return a value for expended circle search.
        mock_db.get_urn_table_mappings = MagicMock()
        mock_db.get_urn_table_mappings.return_value = {'urn1': 'service1', 'urn2': 'service2'}
        mock_db.get_containing_boundary_for_point = MagicMock()
        mock_db.get_containing_boundary_for_point.return_value = []
        mock_db.get_intersecting_boundaries_for_circle = MagicMock()
        mock_db.get_intersecting_boundaries_for_circle.return_value = test_data

        # Set up mock_config to trigger area majority.
        mock_config.do_expanded_search = MagicMock()
        mock_config.do_expanded_search.return_value = True
        mock_config.polygon_multiple_match_policy = MagicMock()
        mock_config.polygon_multiple_match_policy.return_value = \
            lostservice.handling.findservice.PolygonMultipleMatchPolicyEnum.ReturnAreaMajority
        mock_config.expanded_search_buffer = MagicMock()
        mock_config.expanded_search_buffer.return_value = 10
        mock_config.additional_data_uri = MagicMock()
        mock_config.additional_data_uri.return_value = "additional.data.uri"
        mock_config.additional_data_buffer = MagicMock()
        mock_config.additional_data_buffer.return_value = 5.0

        target = lostservice.handling.findservice.FindServiceInner(mock_config, mock_db)
        target._apply_point_multiple_match_policy = MagicMock()
        target._apply_polygon_multiple_match_policy = MagicMock()
        target._apply_polygon_multiple_match_policy.return_value = test_data
        target._apply_policies = MagicMock()
        target._apply_policies.return_value = test_data

        actual = target.find_service_for_point('urn1', 0.0, 1.1, 'something', False)

        self.assertListEqual(actual, test_data)
        mock_config.do_expanded_search.assert_called_once()
        mock_config.polygon_multiple_match_policy.assert_called_once()
        mock_config.expanded_search_buffer.assert_called_once()
        mock_config.additional_data_uri.assert_called_once()
        mock_db.get_containing_boundary_for_point.assert_called_with(
            0.0,
            1.1,
            'something',
            'service1',
            add_data_requested=False,
            buffer_distance = 5.0)
        mock_db.get_containing_boundary_for_point.assert_called_once()



        mock_db.get_intersecting_boundaries_for_circle.assert_called_with(0.0, 1.1, 'something', 10, None, 'service1', True, False)
        mock_db.get_intersecting_boundaries_for_circle.assert_called_once()

        target._apply_point_multiple_match_policy.assert_not_called()
        target._apply_polygon_multiple_match_policy.assert_called_with(test_data)
        target._apply_polygon_multiple_match_policy.assert_called_once()
        target._apply_policies.assert_called_with(test_data, False)
        target._apply_policies.assert_called_once()

    @patch('lostservice.handling.findservice.FindServiceConfigWrapper')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_find_service_for_circle(self, mock_config, mock_db):
        test_data = [{'id': 1, 'AREA_RET': 2}, {'id': 2, 'AREA_RET': 10}, {'id': 1, 'AREA_RET': 5}]

        mock_config.polygon_multiple_match_policy = MagicMock()
        mock_config.polygon_multiple_match_policy.return_value = \
            lostservice.handling.findservice.PolygonMultipleMatchPolicyEnum.ReturnAreaMajority

        mock_db.get_urn_table_mappings = MagicMock()
        mock_db.get_urn_table_mappings.return_value = {'urn1': 'service1', 'urn2': 'service2'}
        mock_db.get_intersecting_boundaries_for_circle = MagicMock()
        mock_db.get_intersecting_boundaries_for_circle.return_value = test_data

        target = lostservice.handling.findservice.FindServiceInner(mock_config, mock_db)
        target._apply_polygon_multiple_match_policy = MagicMock()
        target._apply_polygon_multiple_match_policy.return_value = test_data
        target._apply_policies = MagicMock()
        target._apply_policies.return_value = test_data

        actual = target.find_service_for_circle('urn1', 0.0, 1.1, 'something', 10, 'something else', False)

        self.assertListEqual(actual, test_data)
        mock_config.polygon_multiple_match_policy.assert_called_once()
        mock_db.get_intersecting_boundaries_for_circle.assert_called_with(0.0, 1.1, 'something', 10, 'something else', 'service1', True, False)
        mock_db.get_intersecting_boundaries_for_circle.assert_called_once()
        target._apply_polygon_multiple_match_policy.assert_called_with(test_data)
        target._apply_polygon_multiple_match_policy.assert_called_once()
        target._apply_policies.assert_called_with(test_data, False)
        target._apply_policies.assert_called_once()

    @patch('lostservice.handling.findservice.FindServiceConfigWrapper')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_find_service_for_circle_expanded(self, mock_config, mock_db):
        test_data = [{'id': 1, 'AREA_RET': 2}, {'id': 2, 'AREA_RET': 10}, {'id': 1, 'AREA_RET': 5}]

        mock_config.polygon_multiple_match_policy = MagicMock()
        mock_config.polygon_multiple_match_policy.return_value = \
            lostservice.handling.findservice.PolygonMultipleMatchPolicyEnum.ReturnFirst
        mock_config.do_expanded_search = MagicMock()
        mock_config.do_expanded_search.return_value = True
        mock_config.expanded_search_buffer = MagicMock()
        mock_config.expanded_search_buffer.return_value = 10

        mock_db.get_urn_table_mappings = MagicMock()
        mock_db.get_urn_table_mappings.return_value = {'urn1': 'service1', 'urn2': 'service2'}
        mock_db.get_intersecting_boundaries_for_circle = MagicMock()
        mock_db.get_intersecting_boundaries_for_circle.return_value = []

        target = lostservice.handling.findservice.FindServiceInner(mock_config, mock_db)
        target._apply_polygon_multiple_match_policy = MagicMock()
        target._apply_polygon_multiple_match_policy.return_value = test_data
        target._apply_policies = MagicMock()
        target._apply_policies.return_value = test_data

        actual = target.find_service_for_circle('urn1', 0.0, 1.1, 'something', 10, 'something else', False)

        self.assertListEqual(actual, test_data)
        mock_config.polygon_multiple_match_policy.assert_called_once()
        mock_config.do_expanded_search.assert_called_once()
        mock_config.expanded_search_buffer.assert_called_once()

        calls = [
            call(0.0, 1.1, 'something', 10, 'something else', 'service1', False, False),
            call(0.0, 1.1, 'something', 10, 'something else', 'service1', False, False, True, 10)
        ]

        mock_db.get_intersecting_boundaries_for_circle.assert_has_calls(calls, any_order=False)
        mock_db.get_intersecting_boundaries_for_circle.assert_called()
        target._apply_polygon_multiple_match_policy.assert_called_with([])
        target._apply_polygon_multiple_match_policy.assert_called_once()
        target._apply_policies.assert_called_with(test_data, False)
        target._apply_policies.assert_called_once()

    @patch('lostservice.handling.findservice.FindServiceConfigWrapper')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_find_service_for_ellipse(self, mock_config, mock_db):
        test_data = [{'id': 1, 'AREA_RET': 2}, {'id': 2, 'AREA_RET': 10}, {'id': 1, 'AREA_RET': 5}]

        mock_config.polygon_multiple_match_policy = MagicMock()
        mock_config.polygon_multiple_match_policy.return_value = \
            lostservice.handling.findservice.PolygonMultipleMatchPolicyEnum.ReturnAreaMajority

        mock_db.get_urn_table_mappings = MagicMock()
        mock_db.get_urn_table_mappings.return_value = {'urn1': 'service1', 'urn2': 'service2'}
        mock_db.get_intersecting_boundary_for_ellipse = MagicMock()
        mock_db.get_intersecting_boundary_for_ellipse.return_value = test_data

        target = lostservice.handling.findservice.FindServiceInner(mock_config, mock_db)
        target._apply_polygon_multiple_match_policy = MagicMock()
        target._apply_polygon_multiple_match_policy.return_value = test_data
        target._apply_policies = MagicMock()
        target._apply_policies.return_value = test_data

        actual = target.find_service_for_ellipse('urn1', 0.0, 1.1, 'something', 20.0, 10.0, 90.0, False)

        self.assertListEqual(actual, test_data)
        mock_config.polygon_multiple_match_policy.assert_not_called()
        mock_db.get_intersecting_boundary_for_ellipse.assert_called_with(0.0, 1.1, 'something', 20, 10, 90,
                                                                          'service1')
        mock_db.get_intersecting_boundary_for_ellipse.assert_called_once()
        target._apply_polygon_multiple_match_policy.assert_called_with(test_data)
        target._apply_polygon_multiple_match_policy.assert_called_once()
        target._apply_policies.assert_called_with(test_data, False)
        target._apply_policies.assert_called_once()

    @patch('lostservice.handling.findservice.FindServiceConfigWrapper')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_find_service_for_ellipse_expanded(self, mock_config, mock_db):
        test_data = [{'id': 1, 'AREA_RET': 2}, {'id': 2, 'AREA_RET': 10}, {'id': 1, 'AREA_RET': 5}]

        mock_config.polygon_multiple_match_policy = MagicMock()
        mock_config.polygon_multiple_match_policy.return_value = \
            lostservice.handling.findservice.PolygonMultipleMatchPolicyEnum.ReturnFirst
        mock_config.do_expanded_search = MagicMock()
        mock_config.do_expanded_search.return_value = True
        mock_config.expanded_search_buffer = MagicMock()
        mock_config.expanded_search_buffer.return_value = 10

        mock_db.get_urn_table_mappings = MagicMock()
        mock_db.get_urn_table_mappings.return_value = {'urn1': 'service1', 'urn2': 'service2'}
        mock_db.get_intersecting_boundary_for_ellipse = MagicMock()
        mock_db.get_intersecting_boundary_for_ellipse.return_value = []

        target = lostservice.handling.findservice.FindServiceInner(mock_config, mock_db)
        target._apply_polygon_multiple_match_policy = MagicMock()
        target._apply_polygon_multiple_match_policy.return_value = test_data
        target._apply_policies = MagicMock()
        target._apply_policies.return_value = test_data

        actual = target.find_service_for_ellipse('urn1', 0.0, 1.1, 'something', 20.0, 10.0, 90.0, False)

        self.assertListEqual(actual, test_data)
        mock_config.polygon_multiple_match_policy.assert_not_called()
        mock_config.do_expanded_search.assert_called_once()
        mock_config.expanded_search_buffer.assert_called_once()

        calls = [
            call(0.0, 1.1, 'something', 20.0, 10.0, 90.0, 'service1'),
            call(0.0, 1.1, 'something', 30.0, 20.0, 90.0, 'service1')
        ]

        mock_db.get_intersecting_boundary_for_ellipse.assert_has_calls(calls, any_order=False)
        mock_db.get_intersecting_boundary_for_ellipse.assert_called()
        target._apply_polygon_multiple_match_policy.assert_called_with([])
        target._apply_polygon_multiple_match_policy.assert_called_once()
        target._apply_policies.assert_called_with(test_data, False)
        target._apply_policies.assert_called_once()

    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_find_service_for_arcband(self, mock_db):
        mock_db.get_urn_table_mappings = MagicMock()
        mock_db.get_urn_table_mappings.return_value = {'urn1': 'service1', 'urn2': 'service2'}

        expected = [{'id': 1, 'AREA_RET': 2}, {'id': 2, 'AREA_RET': 10}, {'id': 1, 'AREA_RET': 5}]

        target = lostservice.handling.findservice.FindServiceInner(None, mock_db)
        target.find_service_for_polygon = MagicMock()
        target.find_service_for_polygon.return_value = expected

        actual = target.find_service_for_arcband('urn1', 0.0, 1.1, 'urn:ogc:def:crs:EPSG::4326', 20.0, 90.0, 10.0, 20.0, False)

        self.assertListEqual(actual, expected)
        target.find_service_for_polygon.assert_called_once()

    @patch('lostservice.handling.findservice.FindServiceConfigWrapper')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_find_service_for_polygon_centroid(self, mock_config, mock_db):
        mock_db.get_urn_table_mappings = MagicMock()
        mock_db.get_urn_table_mappings.return_value = {'urn1': 'service1', 'urn2': 'service2'}

        mock_config.polygon_search_mode_policy = MagicMock()
        mock_config.polygon_search_mode_policy.return_value = \
            lostservice.handling.findservice.PolygonSearchModePolicyEnum.SearchUsingCentroid

        expected = [{'id': 1, 'AREA_RET': 2}, {'id': 2, 'AREA_RET': 10}, {'id': 1, 'AREA_RET': 5}]

        target = lostservice.handling.findservice.FindServiceInner(mock_config, mock_db)
        target.find_service_for_point = MagicMock()
        target.find_service_for_point.return_value = expected

        points = [[0, 0], [2, 0], [2, 2], [0, 2]]

        actual = target.find_service_for_polygon('urn1', points, 'something', False)

        self.assertListEqual(actual, expected)
        mock_config.polygon_search_mode_policy.assert_called_once()
        target.find_service_for_point.assert_called_once()
        target.find_service_for_point.assert_called_with('urn1', 1.0, 1.0, 'something', False)

    @patch('lostservice.handling.findservice.FindServiceConfigWrapper')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_find_service_for_polygon(self, mock_config, mock_db):
        expected = [{'id': 1, 'AREA_RET': 2}, {'id': 2, 'AREA_RET': 10}, {'id': 1, 'AREA_RET': 5}]

        mock_db.get_urn_table_mappings = MagicMock()
        mock_db.get_urn_table_mappings.return_value = {'urn1': 'service1', 'urn2': 'service2'}
        mock_db.get_intersecting_boundaries_for_polygon = MagicMock()
        mock_db.get_intersecting_boundaries_for_polygon.return_value = expected

        mock_config.polygon_search_mode_policy = MagicMock()
        mock_config.polygon_search_mode_policy.return_value = \
            lostservice.handling.findservice.PolygonSearchModePolicyEnum.SearchUsingPolygon

        target = lostservice.handling.findservice.FindServiceInner(mock_config, mock_db)
        target._apply_polygon_multiple_match_policy = MagicMock()
        target._apply_polygon_multiple_match_policy.return_value = expected
        target._apply_policies = MagicMock()
        target._apply_policies.return_value = expected

        points = [[0, 0], [2, 0], [2, 2], [0, 2]]

        actual = target.find_service_for_polygon('urn1', points, 'something', False)

        self.assertListEqual(actual, expected)
        mock_config.polygon_search_mode_policy.assert_called_once()
        mock_db.get_intersecting_boundaries_for_polygon.assert_called_once()
        mock_db.get_intersecting_boundaries_for_polygon.assert_called_with(points, 'something', 'service1')
        target._apply_polygon_multiple_match_policy.assert_called_once()
        target._apply_polygon_multiple_match_policy.assert_called_with(expected)
        target._apply_policies.assert_called_once()
        target._apply_policies.assert_called_with(expected, False)

    @patch('lostservice.handling.findservice.FindServiceConfigWrapper')
    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_find_service_for_polygon_expanded(self, mock_config, mock_db):
        expected = [{'id': 1, 'AREA_RET': 2}, {'id': 2, 'AREA_RET': 10}, {'id': 1, 'AREA_RET': 5}]

        mock_db.get_urn_table_mappings = MagicMock()
        mock_db.get_urn_table_mappings.return_value = {'urn1': 'service1', 'urn2': 'service2'}
        mock_db.get_intersecting_boundaries_for_polygon = MagicMock()
        mock_db.get_intersecting_boundaries_for_polygon.return_value = []

        mock_config.polygon_search_mode_policy = MagicMock()
        mock_config.polygon_search_mode_policy.return_value = \
            lostservice.handling.findservice.PolygonSearchModePolicyEnum.SearchUsingPolygon
        mock_config.do_expanded_search = MagicMock()
        mock_config.do_expanded_search.return_value = True
        mock_config.expanded_search_buffer = MagicMock()
        mock_config.expanded_search_buffer.return_value = 10.0

        target = lostservice.handling.findservice.FindServiceInner(mock_config, mock_db)

        target._apply_polygon_multiple_match_policy = MagicMock()
        target._apply_polygon_multiple_match_policy.return_value = expected
        target._apply_policies = MagicMock()
        target._apply_policies.return_value = expected

        points = [[0, 0], [2, 0], [2, 2], [0, 2]]

        actual = target.find_service_for_polygon('urn1', points, 'something', False)

        self.assertListEqual(actual, expected)
        mock_config.polygon_search_mode_policy.assert_called_once()
        mock_config.do_expanded_search.assert_called_once()
        mock_config.expanded_search_buffer.assert_called_once()

        calls = [
            call(points, 'something', 'service1'),
            call(points, 'something', 'service1', True, 10.0)
        ]

        mock_db.get_intersecting_boundaries_for_polygon.assert_has_calls(calls)
        target._apply_polygon_multiple_match_policy.assert_called_once()
        target._apply_polygon_multiple_match_policy.assert_called_with([])
        target._apply_policies.assert_called_once()
        target._apply_policies.assert_called_with(expected, False)

    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_get_esb_table(self, mock_db):
        mock_db.get_urn_table_mappings = MagicMock()
        mock_db.get_urn_table_mappings.return_value = {'urn1': 'service1', 'urn2': 'service2'}

        target = lostservice.handling.findservice.FindServiceInner(None, mock_db)

        actual = target._get_esb_table('urn2');
        self.assertEqual(actual, 'service2')

    @patch('lostservice.db.gisdb.GisDbInterface')
    def test_get_esb_table_exception(self, mock_db):
        mock_db.get_urn_table_mappings = MagicMock()
        mock_db.get_urn_table_mappings.return_value = {'urn1': 'service1', 'urn2': 'service2'}

        target = lostservice.handling.findservice.FindServiceInner(None, mock_db)

        with self.assertRaises(lostservice.exception.ServiceNotImplementedException):
            actual = target._get_esb_table('whatever');


if __name__ == '__main__':
    unittest.main()
