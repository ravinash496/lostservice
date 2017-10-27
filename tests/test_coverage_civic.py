#!/usr/bin/env python
# -*- coding: utf-8 -*-


import unittest
from unittest.mock import patch
from unittest.mock import MagicMock, call
import lostservice.coverage.base as cov_base
import lostservice.coverage.civic as cov_civic
import lostservice.model.civic as mod_civic
import lostservice.exception as lost_exp


class CivicCoverageResolverTest(unittest.TestCase):

    def test_build_where_clause_empty(self):
        expected = ''
        target = cov_civic.CivicCoverageResolver(None, None)
        actual = target._build_where_clause()
        self.assertEqual(expected, actual)

    def test_build_where_clause_not_appending_no_value(self):
        expected = '(field_name IS NULL)'
        target = cov_civic.CivicCoverageResolver(None, None)
        actual = target._build_where_clause(field_name='field_name', value=None, appending=False)
        self.assertEqual(expected, actual)

    def test_build_where_clause_not_appending_with_value(self):
        expected = "((field_name IS NULL) OR (field_name = 'field_value'))"
        target = cov_civic.CivicCoverageResolver(None, None)
        actual = target._build_where_clause(field_name='field_name', value='field_value', appending=False)
        self.assertEqual(expected, actual)

    def test_build_where_clause_appending_with_value(self):
        expected = " AND ((field_name IS NULL) OR (field_name = 'field_value'))"
        target = cov_civic.CivicCoverageResolver(None, None)
        actual = target._build_where_clause(field_name='field_name', value='field_value', appending=True)
        self.assertEqual(expected, actual)

    @patch('lostservice.coverage.base.CoverageConfigWrapper')
    def test_build_coverage_query(self, mock_config: cov_base.CoverageConfigWrapper):

        civ_addr = mod_civic.CivicAddress()
        civ_addr.country = 'country'
        civ_addr.a1 = 'a1'
        civ_addr.a2 = 'a2'
        civ_addr.a3 = 'a3'
        civ_addr.a4 = 'a4'
        civ_addr.a5 = 'a5'

        expected = 'SELECT * FROM the_table WHERE clause clause clause clause clause clause '

        mock_config.civic_coverage_table = MagicMock()
        mock_config.civic_coverage_table.return_value = 'the_table'

        target: cov_civic.CivicCoverageResolver = cov_civic.CivicCoverageResolver(mock_config, None)
        target._build_where_clause = MagicMock()
        target._build_where_clause.return_value = 'clause '

        actual = target.build_coverage_query(civ_addr)

        self.assertEqual(expected, actual)

        mock_config.civic_coverage_table.assert_called_once()
        calls = [
            call('country', 'country'),
            call('a1', 'a1', appending=True),
            call('a2', 'a2', appending=True),
            call('a3', 'a3', appending=True),
            call('a4', 'a4', appending=True),
            call('a5', 'a5', appending=True)
        ]
        target._build_where_clause.assert_has_calls(calls)

    def test_get_address_depth_one(self):
        civ_addr = mod_civic.CivicAddress()
        civ_addr.country = 'country'

        target: cov_civic.CivicCoverageResolver = cov_civic.CivicCoverageResolver(None, None)
        target._civic_address = civ_addr

        actual = target._get_address_depth()
        self.assertEqual(1, actual)

    def test_get_address_depth_two(self):
        civ_addr = mod_civic.CivicAddress()
        civ_addr.country = 'country'
        civ_addr.a1 = 'a1'

        target: cov_civic.CivicCoverageResolver = cov_civic.CivicCoverageResolver(None, None)
        target._civic_address = civ_addr

        actual = target._get_address_depth()
        self.assertEqual(2, actual)

    def test_get_address_depth_three(self):
        civ_addr = mod_civic.CivicAddress()
        civ_addr.country = 'country'
        civ_addr.a1 = 'a1'
        civ_addr.a2 = 'a2'

        target: cov_civic.CivicCoverageResolver = cov_civic.CivicCoverageResolver(None, None)
        target._civic_address = civ_addr

        actual = target._get_address_depth()
        self.assertEqual(3, actual)

    def test_get_address_depth_four(self):
        civ_addr = mod_civic.CivicAddress()
        civ_addr.country = 'country'
        civ_addr.a1 = 'a1'
        civ_addr.a2 = 'a2'
        civ_addr.a3 = 'a3'

        target: cov_civic.CivicCoverageResolver = cov_civic.CivicCoverageResolver(None, None)
        target._civic_address = civ_addr

        actual = target._get_address_depth()
        self.assertEqual(4, actual)

    def test_get_address_depth_five(self):
        civ_addr = mod_civic.CivicAddress()
        civ_addr.country = 'country'
        civ_addr.a1 = 'a1'
        civ_addr.a2 = 'a2'
        civ_addr.a3 = 'a3'
        civ_addr.a4 = 'a4'

        target: cov_civic.CivicCoverageResolver = cov_civic.CivicCoverageResolver(None, None)
        target._civic_address = civ_addr

        actual = target._get_address_depth()
        self.assertEqual(5, actual)

    def test_get_address_depth_six(self):
        civ_addr = mod_civic.CivicAddress()
        civ_addr.country = 'country'
        civ_addr.a1 = 'a1'
        civ_addr.a2 = 'a2'
        civ_addr.a3 = 'a3'
        civ_addr.a4 = 'a4'
        civ_addr.a5 = 'a5'

        target: cov_civic.CivicCoverageResolver = cov_civic.CivicCoverageResolver(None, None)
        target._civic_address = civ_addr

        actual = target._get_address_depth()
        self.assertEqual(6, actual)

    def test_get_match_null_count(self):
        match = {}
        target: cov_civic.CivicCoverageResolver = cov_civic.CivicCoverageResolver(None, None)
        actual = target._get_match_null_count(match)
        self.assertEqual(6, actual)
        self.assertDictEqual(match, {'null_count': 6})

    def test_get_match_depth(self):

        match = {}
        expected_match = {}

        target: cov_civic.CivicCoverageResolver = cov_civic.CivicCoverageResolver(None, None)

        actual = target._get_match_depth(6, match)
        expected_match['match_depth'] = 0
        self.assertEqual(0, actual)
        self.assertDictEqual(match, expected_match)

        match['country'] = 'country'
        expected_match.update(match)
        expected_match['match_depth'] = 1
        actual = target._get_match_depth(6, match)
        self.assertEqual(1, actual)
        self.assertDictEqual(match, expected_match)

        match['a1'] = 'a1'
        expected_match.update(match)
        expected_match['match_depth'] = 2
        actual = target._get_match_depth(6, match)
        self.assertEqual(2, actual)
        self.assertDictEqual(match, expected_match)

        match['a2'] = 'a2'
        expected_match.update(match)
        expected_match['match_depth'] = 3
        actual = target._get_match_depth(6, match)
        self.assertEqual(3, actual)
        self.assertDictEqual(match, expected_match)

        match['a3'] = 'a3'
        expected_match.update(match)
        expected_match['match_depth'] = 4
        actual = target._get_match_depth(6, match)
        self.assertEqual(4, actual)
        self.assertDictEqual(match, expected_match)

        match['a4'] = 'a4'
        expected_match.update(match)
        expected_match['match_depth'] = 5
        actual = target._get_match_depth(6, match)
        self.assertEqual(5, actual)
        self.assertDictEqual(match, expected_match)

        match['a5'] = 'a5'
        expected_match.update(match)
        expected_match['match_depth'] = 6
        actual = target._get_match_depth(6, match)
        self.assertEqual(6, actual)
        self.assertDictEqual(match, expected_match)

    def test_get_best_match(self):

        input_matches = [
            {'country': 'USA', 'a1': 'a1', 'a2': None, 'a3': None, 'a4': None, 'a5': None},
            {'country': 'USA', 'a1': 'a1', 'a2': 'a2', 'a3': None, 'a4': None, 'a5': None},
            {'country': 'USA', 'a1': 'a1', 'a2': 'a2', 'a3': 'a3', 'a4': None, 'a5': None},
            {'country': 'USA', 'a1': 'a1', 'a2': 'a2', 'a3': 'a3', 'a4': 'a4', 'a5': None}
        ]

        expected = {
            'country': 'USA',
            'a1': 'a1',
            'a2': 'a2',
            'a3': 'a3',
            'a4': 'a4',
            'a5': None,
            'match_depth': 5,
            'null_count': 1
        }

        target: cov_civic.CivicCoverageResolver = cov_civic.CivicCoverageResolver(None, None)
        target._get_address_depth = MagicMock()
        target._get_address_depth.return_value = 5

        actual = target._get_best_match(input_matches)

        self.assertDictEqual(expected, actual)

    @patch('lostservice.coverage.base.CoverageConfigWrapper')
    def test_build_response_with_result(self, mock_config: cov_base.CoverageConfigWrapper):

        input_matches = [
            {'country': 'USA', 'a1': 'a1', 'a2': None, 'a3': None, 'a4': None, 'a5': None, 'lostserver': 'one'},
            {'country': 'USA', 'a1': 'a1', 'a2': 'a2', 'a3': None, 'a4': None, 'a5': None, 'lostserver': 'two'},
            {'country': 'USA', 'a1': 'a1', 'a2': 'a2', 'a3': 'a3', 'a4': None, 'a5': None, 'lostserver': 'three'},
            {'country': 'USA', 'a1': 'a1', 'a2': 'a2', 'a3': 'a3', 'a4': 'a4', 'a5': None, 'lostserver': 'four'}
        ]

        target: cov_civic.CivicCoverageResolver = cov_civic.CivicCoverageResolver(mock_config, None)
        target._get_address_depth = MagicMock()
        target._get_address_depth.return_value = 5

        actual = target.build_response(input_matches)
        self.assertEqual('four', actual)

        target._get_address_depth.assert_called_once()

    @patch('lostservice.coverage.base.CoverageConfigWrapper')
    def test_build_response_without_result_return_parent(self, mock_config: cov_base.CoverageConfigWrapper):
        input_matches = []

        mock_config.parent_ecrf = MagicMock()
        mock_config.parent_ecrf.return_value = 'some.parent.ecrf'

        target: cov_civic.CivicCoverageResolver = cov_civic.CivicCoverageResolver(mock_config, None)

        actual = target.build_response(input_matches)
        self.assertEqual('some.parent.ecrf', actual)
        mock_config.parent_ecrf.assert_called_once()

    @patch('lostservice.coverage.base.CoverageConfigWrapper')
    def test_build_response_without_result_no_parent(self, mock_config: cov_base.CoverageConfigWrapper):
        input_matches = []

        mock_config.parent_ecrf = MagicMock()
        mock_config.parent_ecrf.return_value = None

        target: cov_civic.CivicCoverageResolver = cov_civic.CivicCoverageResolver(mock_config, None)

        with self.assertRaises(lost_exp.NotFoundException):
            actual = target.build_response(input_matches)

        mock_config.parent_ecrf.assert_called_once()


if __name__ == '__main__':
    unittest.main()
