#!/usr/bin/env python
# -*- coding: utf-8 -*-


import unittest
from unittest.mock import patch
from unittest.mock import MagicMock
import civvy.db.postgis.query as civvy_pg
import lostservice.coverage.base as cov_base


class CoverageBaseTest(unittest.TestCase):

    @patch('lostservice.coverage.base.CoverageConfigWrapper')
    @patch('civvy.db.postgis.query.PgQueryExecutor')
    def test_build_execute(self, mock_config: cov_base.CoverageConfigWrapper, mock_pg_exec: civvy_pg.PgQueryExecutor):

        exec_input = 'here is a thing'
        query_string = 'select * from whatever'
        query_result = {'field1': 'value1', 'field2': 'value2'}
        expected = 'here.is.a.result'

        mock_pg_exec.execute = MagicMock()
        mock_pg_exec.execute.return_value = query_result

        target = cov_base.CoverageBase(mock_config, mock_pg_exec)
        target.build_coverage_query = MagicMock()
        target.build_coverage_query.return_value = query_string
        target.build_response = MagicMock()
        target.build_response.return_value = expected

        actual = target.execute(exec_input)

        target.build_coverage_query.assert_called_once()
        target.build_coverage_query.assert_called_with(exec_input)

        mock_pg_exec.execute.assert_called_once()
        mock_pg_exec.execute.assert_called_with(query_string)

        target.build_response.assert_called_once()
        target.build_response.assert_called_with(query_result)

        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
