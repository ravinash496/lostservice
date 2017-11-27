#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from unittest.mock import patch
from unittest.mock import MagicMock
import lostservice.handling.core
import lostservice.handling.findservice
import lostservice.model.requests
import lostservice.model.responses
import lostservice.model.location


class FindServiceOuterTest(unittest.TestCase):

    @patch('lostservice.handling.findservice.FindServiceConfigWrapper')
    @patch('lostservice.handling.findservice.FindServiceInner')
    def test_point(self, mock_config, mock_inner):

        mock_config.source_uri = MagicMock()
        mock_config.source_uri.return_value = 'foo'

        mock_inner.find_service_for_point = MagicMock()
        mock_inner.find_service_for_point.return_value = []

        mock_inner.fuzzy_used = MagicMock()
        mock_inner.fuzzy_used = False

        model = lostservice.model.requests.FindServiceRequest()
        model.serviceBoundary = 'reference'
        model.service = 'some:service:urn'
        model.path = ['path.one', 'path.two']
        model.location = lostservice.model.location.Location()
        model.location.id = '1234'
        model.location.location = lostservice.model.geodetic.Point()
        model.location.location.longitude = 0.0
        model.location.location.latitude = 0.0
        model.location.location.spatial_ref = 'bar::4321'

        target = lostservice.handling.findservice.FindServiceOuter(mock_config, mock_inner)

        try:
            actual = target.find_service_for_point(model)
            mock_inner.find_service_for_point.assert_called_once()
            mock_inner.find_service_for_point.assert_called_with(model.service,
                                                                 model.location.location,
                                                                 False)
            self.assertListEqual(actual.path, ['path.one', 'path.two', 'foo'])
            self.assertListEqual(actual.nonlostdata, [])
            self.assertListEqual(actual.mappings, [])
            self.assertEqual(actual.location_used, '1234')

        except:
            self.fail("handle_request threw an exception.")

    @patch('lostservice.handling.findservice.FindServiceConfigWrapper')
    @patch('lostservice.handling.findservice.FindServiceInner')
    def test_circle(self, mock_config, mock_inner):

        mock_config.source_uri = MagicMock()
        mock_config.source_uri.return_value = 'foo'

        mock_config.service_boundary_return_geodetic_override = MagicMock()
        mock_config.service_boundary_return_geodetic_override.return_value = \
            lostservice.handling.findservice.ServiceBoundaryGeodeticOverridePolicyEnum.MatchRequest

        mock_inner.find_service_for_circle = MagicMock()
        mock_inner.find_service_for_circle.return_value = []

        mock_inner.fuzzy_used = MagicMock()
        mock_inner.fuzzy_used = False

        model = lostservice.model.requests.FindServiceRequest()
        model.serviceBoundary = 'value'
        model.service = 'some:service:urn'
        model.path = ['path.one']
        model.location = lostservice.model.location.Location()
        model.location.id = '1234'
        model.location.location = lostservice.model.geodetic.Circle()
        model.location.location.longitude = 0.0
        model.location.location.latitude = 0.0
        model.location.location.spatial_ref = 'bar::4321'
        model.location.location.radius = '1.1'
        model.location.location.uom = 'baz'
        model.nonlostdata = ['non-lost-data']

        target = lostservice.handling.findservice.FindServiceOuter(mock_config, mock_inner)

        try:
            actual = target.find_service_for_circle(model)
            mock_inner.find_service_for_circle.assert_called_once()
            mock_inner.find_service_for_circle.assert_called_with(model.service,
                                                                  model.location.location,
                                                                  True)

            self.assertListEqual(actual.path, ['path.one', 'foo'])
            self.assertListEqual(actual.nonlostdata, ['non-lost-data'])
            self.assertListEqual(actual.mappings, [])
            self.assertEqual(actual.location_used, '1234')

        except:
            self.fail("handle_request threw an exception.")

    @patch('lostservice.handling.findservice.FindServiceConfigWrapper')
    @patch('lostservice.handling.findservice.FindServiceInner')
    def test_ellipse(self, mock_config, mock_inner):

        mock_config.source_uri = MagicMock()
        mock_config.source_uri.return_value = 'foo'

        mock_config.service_boundary_return_geodetic_override = MagicMock()
        mock_config.service_boundary_return_geodetic_override.return_value = \
            lostservice.handling.findservice.ServiceBoundaryGeodeticOverridePolicyEnum.MatchRequest

        mock_inner.find_service_for_ellipse = MagicMock()
        mock_inner.find_service_for_ellipse.return_value = []

        mock_inner.fuzzy_used = MagicMock()
        mock_inner.fuzzy_used = False

        model = lostservice.model.requests.FindServiceRequest()
        model.serviceBoundary = 'value'
        model.service = 'some:service:urn'
        model.path = []
        model.location = lostservice.model.location.Location()
        model.location.id = '1234'
        model.location.location = lostservice.model.geodetic.Ellipse()
        model.location.location.longitude = 0.0
        model.location.location.latitude = 0.0
        model.location.location.spatial_ref = 'bar::4321'
        model.location.location.majorAxis = '1.1'
        model.location.location.minorAxis = '2.2'
        model.location.location.orientation = '3.3'
        model.location.location.uom = 'baz'
        model.nonlostdata = ['non-lost-data', 'more-non-lost-data']

        target = lostservice.handling.findservice.FindServiceOuter(mock_config, mock_inner)

        try:
            actual = target.find_service_for_ellipse(model)
            mock_inner.find_service_for_ellipse.assert_called_once()
            mock_inner.find_service_for_ellipse.assert_called_with(model.service,
                                                                   model.location.location,
                                                                   True)

            self.assertListEqual(actual.path, ['foo'])
            self.assertListEqual(actual.nonlostdata, ['non-lost-data', 'more-non-lost-data'])
            self.assertListEqual(actual.mappings, [])
            self.assertEqual(actual.location_used, '1234')

        except:
            self.fail("handle_request threw an exception.")

    @patch('lostservice.handling.findservice.FindServiceConfigWrapper')
    @patch('lostservice.handling.findservice.FindServiceInner')
    def test_arcband(self, mock_config, mock_inner):

        mock_config.source_uri = MagicMock()
        mock_config.source_uri.return_value = 'foo'

        mock_inner.find_service_for_arcband = MagicMock()
        mock_inner.find_service_for_arcband.return_value = []

        mock_inner.fuzzy_used = MagicMock()
        mock_inner.fuzzy_used = False

        model = lostservice.model.requests.FindServiceRequest()
        model.serviceBoundary = 'reference'
        model.service = 'some:service:urn'
        model.path = []
        model.location = lostservice.model.location.Location()
        model.location.id = '1234'
        model.location.location = lostservice.model.geodetic.Arcband()
        model.location.location.longitude = 0.0
        model.location.location.latitude = 0.0
        model.location.location.spatial_ref = 'bar::4321'
        model.location.location.start_angle = '1.1'
        model.location.location.opening_angle = '2.2'
        model.location.location.inner_radius = '3.3'
        model.location.location.outer_radius = '4.4'
        model.location.location.uom = 'baz'
        model.nonlostdata = ['non-lost-data', 'more-non-lost-data', 'still-more-non-lost-data']
        target = lostservice.handling.findservice.FindServiceOuter(mock_config, mock_inner)

        try:
            actual = target.find_service_for_arcband(model)
            mock_inner.find_service_for_arcband.assert_called_once()
            mock_inner.find_service_for_arcband.assert_called_with(model.service,
                                                                   model.location.location,
                                                                   False)

            self.assertListEqual(actual.path, ['foo'])
            self.assertListEqual(actual.nonlostdata,
                                 ['non-lost-data', 'more-non-lost-data', 'still-more-non-lost-data'])
            self.assertListEqual(actual.mappings, [])
            self.assertEqual(actual.location_used, '1234')

        except:
            self.fail("handle_request threw an exception.")

    @patch('lostservice.handling.findservice.FindServiceConfigWrapper')
    @patch('lostservice.handling.findservice.FindServiceInner')
    def test_polygon(self, mock_config, mock_inner):

        mock_config.source_uri = MagicMock()
        mock_config.source_uri.return_value = 'foo'

        mock_inner.find_service_for_polygon = MagicMock()
        mock_inner.find_service_for_polygon.return_value = []

        mock_inner.fuzzy_used = MagicMock()
        mock_inner.fuzzy_used = False

        model = lostservice.model.requests.FindServiceRequest()
        model.serviceBoundary = 'reference'
        model.service = 'some:service:urn'
        model.path = []
        model.location = lostservice.model.location.Location()
        model.location.id = '1234'
        model.location.location = lostservice.model.geodetic.Polygon()
        model.location.location.vertices = [[1, 1], [2, 2], [3, 3]]
        model.location.location.spatial_ref = 'bar::1234'
        model.nonlostdata = []
        target = lostservice.handling.findservice.FindServiceOuter(mock_config, mock_inner)

        try:
            actual = target.find_service_for_polygon(model)
            mock_inner.find_service_for_polygon.assert_called_once()
            mock_inner.find_service_for_polygon.assert_called_with(model.service,
                                                                   model.location.location,
                                                                   False)

            self.assertListEqual(actual.path, ['foo'])
            self.assertListEqual(actual.nonlostdata, [])
            self.assertListEqual(actual.mappings, [])
            self.assertEqual(actual.location_used, '1234')

        except:
            self.fail("handle_request threw an exception.")

    @patch('lostservice.handling.findservice.FindServiceConfigWrapper')
    def test_build_one_mapping_no_boundary(self, mock_config):

        mapping = {
            'displayname': 'foo',
            'routeuri': 'bar',
            'servicenum': 'baz',
            'srcunqid': '{12345}',
            'serviceurn': 'some.service.urn',
            'updatedate': 'whenever',
            'expiration': 'never'
        }

        mock_config.service_boundary_return_geodetic_override = MagicMock()
        mock_config.service_boundary_return_geodetic_override.return_value = \
            lostservice.handling.findservice.ServiceBoundaryGeodeticOverridePolicyEnum.MatchRequest

        target = lostservice.handling.findservice.FindServiceOuter(mock_config, None)
        actual = target._build_one_mapping(mapping, False)

        self.assertEqual(actual.display_name, mapping['displayname'])
        self.assertEqual(actual.route_uri, mapping['routeuri'])
        self.assertEqual(actual.service_number, mapping['servicenum'])
        self.assertEqual(actual.source_id, mapping['srcunqid'])
        self.assertEqual(actual.service_urn, mapping['serviceurn'])
        self.assertEqual(actual.last_updated, mapping['updatedate'])
        self.assertEqual(actual.expires, mapping['expiration'])
        self.assertEqual(actual.boundary_value, '')

    @patch('lostservice.handling.findservice.FindServiceConfigWrapper')
    def test_build_one_mapping_with_boundary(self, mock_config):

        mapping = {
            'displayname': 'foo',
            'routeuri': 'bar',
            'servicenum': 'baz',
            'srcunqid': '{12345}',
            'serviceurn': 'some.service.urn',
            'updatedate': 'whenever',
            'expiration': 'never',
            'ST_AsGML_1': '<GML />'
        }

        mock_config.service_boundary_return_geodetic_override = MagicMock()
        mock_config.service_boundary_return_geodetic_override.return_value = \
            lostservice.handling.findservice.ServiceBoundaryGeodeticOverridePolicyEnum.MatchRequest

        target = lostservice.handling.findservice.FindServiceOuter(mock_config, None)
        actual = target._build_one_mapping(mapping, True)

        self.assertEqual(actual.display_name, mapping['displayname'])
        self.assertEqual(actual.route_uri, mapping['routeuri'])
        self.assertEqual(actual.service_number, mapping['servicenum'])
        self.assertEqual(actual.source_id, mapping['srcunqid'])
        self.assertEqual(actual.service_urn, mapping['serviceurn'])
        self.assertEqual(actual.last_updated, mapping['updatedate'])
        self.assertEqual(actual.expires, mapping['expiration'])
        self.assertEqual(actual.boundary_value, mapping['ST_AsGML_1'])

    @patch('lostservice.handling.findservice.FindServiceConfigWrapper')
    def test_build_one_mapping_with_boundary_override_returnNothing(self, mock_config):

        mapping = {
            'displayname': 'foo',
            'routeuri': 'bar',
            'servicenum': 'baz',
            'srcunqid': '{12345}',
            'serviceurn': 'some.service.urn',
            'updatedate': 'whenever',
            'expiration': 'never',
            'ST_AsGML_1': '<GML />'
        }

        mock_config.service_boundary_return_geodetic_override = MagicMock()
        mock_config.service_boundary_return_geodetic_override.return_value = \
            lostservice.handling.findservice.ServiceBoundaryGeodeticOverridePolicyEnum.ReturnNothing

        target = lostservice.handling.findservice.FindServiceOuter(mock_config, None)
        actual = target._build_one_mapping(mapping, True)

        self.assertEqual(actual.display_name, mapping['displayname'])
        self.assertEqual(actual.route_uri, mapping['routeuri'])
        self.assertEqual(actual.service_number, mapping['servicenum'])
        self.assertEqual(actual.source_id, mapping['srcunqid'])
        self.assertEqual(actual.service_urn, mapping['serviceurn'])
        self.assertEqual(actual.last_updated, mapping['updatedate'])
        self.assertEqual(actual.expires, mapping['expiration'])
        self.assertIsNone(actual.boundary_value)


    @patch('lostservice.handling.findservice.FindServiceConfigWrapper')
    def test_build_mapping_list(self, mock_config):

        mock_config.source_uri = MagicMock()
        mock_config.source_uri.return_value = 'foo'

        mappings = [{
            'displayname': 'foo',
            'routeuri': 'bar',
            'servicenum': 'baz',
            'srcunqid': '{12345}',
            'serviceurn': 'some.service.urn',
            'updatedate': 'whenever',
            'expiration': 'never',
            'ST_AsGML_1': '<GML />'
        }]

        target = lostservice.handling.findservice.FindServiceOuter(mock_config, None)
        actual = target._build_mapping_list(mappings, True)

        self.assertEqual(len(actual), 1)
        self.assertEqual(actual[0].source, 'foo')
        self.assertEqual(actual[0].display_name, mappings[0]['displayname'])
        self.assertEqual(actual[0].route_uri, mappings[0]['routeuri'])
        self.assertEqual(actual[0].service_number, mappings[0]['servicenum'])
        self.assertEqual(actual[0].source_id, mappings[0]['srcunqid'])
        self.assertEqual(actual[0].service_urn, mappings[0]['serviceurn'])
        self.assertEqual(actual[0].last_updated, mappings[0]['updatedate'])
        self.assertEqual(actual[0].expires, mappings[0]['expiration'])
        self.assertEqual(actual[0].boundary_value, mappings[0]['ST_AsGML_1'])

    @patch('lostservice.handling.findservice.FindServiceConfigWrapper')
    def test_build_empty_mapping_list(self, mock_config):

        mock_config.source_uri = MagicMock()
        mock_config.source_uri.return_value = 'foo'
        mappings = []
        target = lostservice.handling.findservice.FindServiceOuter(mock_config, None)
        actual = target._build_mapping_list(mappings, True)
        self.assertEqual(len(actual), 0)

    @patch('lostservice.handling.findservice.FindServiceConfigWrapper')
    def test_build_multiple_mapping_list(self, mock_config):

        mock_config.source_uri = MagicMock()
        mock_config.source_uri.return_value = 'foo'

        mappings = [
            {
                'displayname': 'foo',
                'routeuri': 'bar',
                'servicenum': 'baz',
                'srcunqid': '{12345}',
                'serviceurn': 'some.service.urn',
                'updatedate': 'whenever',
                'expiration': 'never',
                'ST_AsGML_1': '<GML />'
            },
            {
                'displayname': 'a',
                'routeuri': 'b',
                'servicenum': 'c',
                'srcunqid': '{9876}',
                'serviceurn': 'some.other.service.urn',
                'updatedate': 'later',
                'expiration': 'before'
            }
        ]

        target = lostservice.handling.findservice.FindServiceOuter(mock_config, None)
        actual = target._build_mapping_list(mappings, True)

        self.assertEqual(len(actual), 2)
        self.assertEqual(actual[0].source, 'foo')
        self.assertEqual(actual[0].display_name, mappings[0]['displayname'])
        self.assertEqual(actual[0].route_uri, mappings[0]['routeuri'])
        self.assertEqual(actual[0].service_number, mappings[0]['servicenum'])
        self.assertEqual(actual[0].source_id, mappings[0]['srcunqid'])
        self.assertEqual(actual[0].service_urn, mappings[0]['serviceurn'])
        self.assertEqual(actual[0].last_updated, mappings[0]['updatedate'])
        self.assertEqual(actual[0].expires, mappings[0]['expiration'])
        self.assertEqual(actual[0].boundary_value, mappings[0]['ST_AsGML_1'])

        self.assertEqual(actual[1].source, 'foo')
        self.assertEqual(actual[1].display_name, mappings[1]['displayname'])
        self.assertEqual(actual[1].route_uri, mappings[1]['routeuri'])
        self.assertEqual(actual[1].service_number, mappings[1]['servicenum'])
        self.assertEqual(actual[1].source_id, mappings[1]['srcunqid'])
        self.assertEqual(actual[1].service_urn, mappings[1]['serviceurn'])
        self.assertEqual(actual[1].last_updated, mappings[1]['updatedate'])
        self.assertEqual(actual[1].expires, mappings[1]['expiration'])

    @patch('lostservice.handling.findservice.FindServiceConfigWrapper')
    def test_build_response(self, mock_config):
        mock_config.source_uri = MagicMock()
        mock_config.source_uri.return_value = 'foo'

        mappings = [{
            'displayname': 'foo',
            'routeuri': 'bar',
            'servicenum': 'baz',
            'srcunqid': '{12345}',
            'serviceurn': 'some.service.urn',
            'updatedate': 'whenever',
            'expiration': 'never',
            'ST_AsGML_1': '<GML />'
        }]

        target = lostservice.handling.findservice.FindServiceOuter(mock_config, None)
        actual = target._build_response(['one', 'two'], '1234567', mappings, ['a', 'b'], True)

        self.assertListEqual(actual.path, ['one', 'two', 'foo'])
        self.assertEqual(actual.location_used, '1234567')
        self.assertEqual(actual.nonlostdata, ['a', 'b'])

        self.assertEqual(len(actual.mappings), 1)
        self.assertEqual(actual.mappings[0].source, 'foo')
        self.assertEqual(actual.mappings[0].display_name, mappings[0]['displayname'])
        self.assertEqual(actual.mappings[0].route_uri, mappings[0]['routeuri'])
        self.assertEqual(actual.mappings[0].service_number, mappings[0]['servicenum'])
        self.assertEqual(actual.mappings[0].source_id, mappings[0]['srcunqid'])
        self.assertEqual(actual.mappings[0].service_urn, mappings[0]['serviceurn'])
        self.assertEqual(actual.mappings[0].last_updated, mappings[0]['updatedate'])
        self.assertEqual(actual.mappings[0].expires, mappings[0]['expiration'])
        self.assertEqual(actual.mappings[0].boundary_value, mappings[0]['ST_AsGML_1'])

    @patch('lostservice.handling.findservice.FindServiceConfigWrapper')
    def test_build_warnings_no_change(self, mock_config):

        mock_config.source_uri = MagicMock()
        mock_config.source_uri.return_value = 'foo'

        mock_config.polygon_multiple_match_policy = MagicMock()
        mock_config.polygon_multiple_match_policy.return_value = \
            lostservice.handling.findservice.PolygonMultipleMatchPolicyEnum.ReturnLimitWarning

        mappings = [{
            'displayname': 'foo',
            'routeuri': 'bar',
            'servicenum': 'baz',
            'srcunqid': '{12345}',
            'serviceurn': 'some.service.urn',
            'updatedate': 'whenever',
            'expiration': 'never',
            'ST_AsGML_1': '<GML />'
        }]

        nonlostdata = ['<notLoST>']

        target = lostservice.handling.findservice.FindServiceOuter(mock_config, None)
        actual = target._build_warnings(mappings, nonlostdata)

        self.assertEqual(len(actual), 1)
        self.assertEqual(actual[0], '<notLoST>')

    @patch('lostservice.handling.findservice.FindServiceConfigWrapper')
    def test_build_warnings_add_warning(self, mock_config):

        mock_config.source_uri = MagicMock()
        mock_config.source_uri.return_value = 'foo'

        mock_config.polygon_multiple_match_policy = MagicMock()
        mock_config.polygon_multiple_match_policy.return_value = \
            lostservice.handling.findservice.PolygonMultipleMatchPolicyEnum.ReturnLimitWarning

        mappings = [{
            'displayname': 'foo',
            'routeuri': 'bar',
            'servicenum': 'baz',
            'srcunqid': '{12345}',
            'serviceurn': 'some.service.urn',
            'updatedate': 'whenever',
            'expiration': 'never',
            'ST_AsGML_1': '<GML />',
            'tooManyMappings': True
        }]

        nonlostdata = ['<notLoST>']

        target = lostservice.handling.findservice.FindServiceOuter(mock_config, None)
        actual = target._build_warnings(mappings, nonlostdata)

        self.assertEqual(len(actual), 2)
        self.assertEqual(actual[0], '<notLoST>')
        self.assertEqual(actual[1].tag, 'warnings')

    @patch('lostservice.handling.findservice.FindServiceConfigWrapper')
    def test_check_is_addurl_in_mappings(self, mock_config):

        mock_config.source_uri = MagicMock()
        mock_config.source_uri.return_value = 'foo'

        mappings = [{
            'servicenum': 'baz',
            'srcunqid': '{12345}',
            'serviceurn': 'some.service.urn',
            'updatedate': 'whenever',
            'expiration': 'never',
            'tooManyMappings': True,
            'adddatauri': "someuri"
        }]

        target = lostservice.handling.findservice.FindServiceOuter(mock_config, None)
        actual = target._check_is_addurl_in_mappings(mappings)
        expected = True

        self.assertEqual(actual, expected)

    @patch('lostservice.handling.findservice.FindServiceConfigWrapper')
    def test_loop_error(self, mock_config):

        mock_config.source_uri = MagicMock()
        mock_config.source_uri.return_value = 'authoritative.example'

        target = lostservice.handling.findservice.FindServiceOuter(mock_config, None)

        try:
            path = ['authoritative.example']
            target._check_is_loopback(path)
        except Exception as e:
            self.assertEqual(str(e),'<loop message="LoopError" xml:lang="en"/>')

if __name__ == '__main__':
    unittest.main()
