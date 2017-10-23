#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: lostservice.coverage.civic
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

Implementation for civic coverage resolver.
"""

from injector import inject
from typing import Iterator, Dict, List
import civvy.db.postgis.query as civvy_pg
import lostservice.coverage.base as base
import lostservice.exception as exp
import lostservice.model.civic as model


class CivicCoverageResolver(base.CoverageBase):
    """
    Class that implements civic coverage resolution

    """

    @inject
    def __init__(self, cov_config: base.CoverageConfigWrapper, query_executor: civvy_pg.PgQueryExecutor):
        """
        Constructor

        :param cov_config: A reference to the CoverageConfig.
        :param query_executor: An instance of a PgQueryExecutor that will perform the query.
        """
        super().__init__(cov_config, query_executor)
        self._civic_address = None

    def _build_where_clause(self, field_name: str=None, value: str=None, appending: bool=False):
        """
        Builds a where clause for the given target and value.

        :param field_name: The target field to match.
        :param value:  The value to match to.
        :param appending: Whether this will be appending to an already existing where clause or not.
        :return: The constructed where clause ready to be dropped into a query.
        """
        where_clause = ''
        if field_name:
            if appending:
                where_clause += ' AND '

            if value:
                where_clause += "(({0} IS NULL) OR ({0} = {1}))".format(field_name, value)
            else:
                where_clause += "({0} IS NULL)".format(field_name)

        return where_clause

    def build_coverage_query(self, civic_addr: model.CivicAddress) -> str:
        """
        Build the query string for the given address.

        :param civic_addr: The civic address model.
        :return: The
        """
        # cache the address so we can use it when building the response.
        self._civic_address = civic_addr

        table_name = self._config.civic_coverage_table()
        where_clause = ''

        where_clause += self._build_where_clause('country', civic_addr.country)
        where_clause += self._build_where_clause('a1', civic_addr.a1)
        where_clause += self._build_where_clause('a2', civic_addr.a2)
        where_clause += self._build_where_clause('a3', civic_addr.a3)
        where_clause += self._build_where_clause('a4', civic_addr.a4)
        where_clause += self._build_where_clause('a5', civic_addr.a5)

        sql_query = "SELECT * FROM {0} WHERE ".format(table_name) + where_clause

        return sql_query

    def _get_address_depth(self) -> int:
        """
        Calculates the depth of the given civic address.

        :param civic_addr: The civic address model
        :return: The depth.
        """
        depth = 0
        if self._civic_addr:
            if self._civic_addr.a5:
                depth = 6
            elif self._civic_addr.a4:
                depth = 5
            elif self._civic_addr.a3:
                depth = 4
            elif self._civic_addr.a2:
                depth = 3
            elif self._civic_addr.a1:
                depth = 2
            elif self._civic_addr.country:
                depth = 1

        return depth

    def _get_match_null_count(self, match: Dict) -> int:
        """
        Gets the count of nulls in the matched address.

        :param match: The dictionary of values for the match.
        :return: The number of nulls.
        """
        null_count = 0
        if match['a5']:
            null_count += 1
        elif match['a4']:
            null_count += 1
        elif match['a3']:
            null_count += 1
        elif match['a2']:
            null_count += 1
        elif match['a1']:
            null_count += 1
        elif match['country']:
            null_count += 1

        match['null_count'] = null_count
        return null_count

    def _get_match_depth(self, civic_depth, match: Dict) -> int:
        """
        Add the match depth to the given match.

        :param civic_depth: The depth of the civic address.
        :param match: The dictionary of values for the match.
        :return: The match depth.
        """
        # This is stupid and we should find a better way to do it.
        match_depth = 0

        if civic_depth == 6:
            if match['a5']:
                match_depth = 6
            elif match['a4']:
                match_depth = 5
            elif match['a3']:
                match_depth = 4
            elif match['a2']:
                match_depth = 3
            elif match['a1']:
                match_depth = 2
            elif match['country']:
                match_depth = 1
        elif civic_depth == 5:
            if match['a4']:
                match_depth = 5
            elif match['a3']:
                match_depth = 4
            elif match['a2']:
                match_depth = 3
            elif match['a1']:
                match_depth = 2
            elif match['country']:
                match_depth = 1
        elif civic_depth == 4:
            if match['a3']:
                match_depth = 4
            elif match['a2']:
                match_depth = 3
            elif match['a1']:
                match_depth = 2
            elif match['country']:
                match_depth = 1
        elif civic_depth == 3:
            if match['a2']:
                match_depth = 3
            elif match['a1']:
                match_depth = 2
            elif match['country']:
                match_depth = 1
        elif civic_depth == 2:
            if match['a1']:
                match_depth = 2
            elif match['country']:
                match_depth = 1
        elif civic_depth == 1:
            if match['country']:
                match_depth = 1

        match['match_depth'] = match_depth
        return match_depth

    def _get_best_match(self, matches: List) -> Dict:
        """
        Sort the matches by coverage match depth.

        :param matches: The matches.
        :return: The matches
        """
        address_depth = self._get_address_depth()

        for match in matches:
            self._get_match_depth(address_depth, match)
            self._get_match_null_count(match)

        # Sort the matches by match depth.
        sorted_matches = sorted(matches, key=lambda k: k['match_depth'])
        # Pull of the value of the best match.
        best_match_value = sorted_matches[0]['match_depth']
        # Now filter the list to only those that have a match depth equal to the best.
        best_matches = filter(lambda m: m['match_depth'] == best_match_value, sorted_matches)
        # Sort all of the tied best matches based on lowest null count.
        sorted_best_matches = sorted(best_matches, key=lambda k: k['null_count'], reverse=True)
        # Return the best one.
        return sorted_best_matches[0]

    def build_response(self, result: Iterator[dict]) -> str:
        """
        Abstract method for building the response to the query given the result which will be specific to the
        specific coverage implementation.

        :param result: The result of query execution.
        :return: The coverage response.
        """
        result_list = list(result)
        if result_list:
            best_match = self._get_best_match(result_list)
            return best_match['lostserver']
        else:
            # There were no results, so we either return the parent, if there is one,
            # or we return a not found exception.
            parent = self._config.parent_ecrf()
            if parent:
                return parent
            else:
                raise exp.NotFoundException('The given address does not match known coverage regions.')
