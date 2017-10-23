#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: lostservice.coverage.base
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

Base class(es) for coverage support.
"""

from abc import ABCMeta, abstractmethod
from injector import inject
from typing import Iterator
import civvy.db.postgis.query as civvy_pg
import lostservice.configuration as lost_config


class CoverageConfigWrapper(object):
    """
    A wrapper class for Coverage configuration related information.

    """

    @inject
    def __init__(self, config: lost_config.Configuration):
        """
        Constructor.

        :param config: The configuration object.
        :type config: :py:class:`lostservice.configuration.Configuration`
        """
        self._config = config

    def do_coverage(self) -> bool:
        """
        Checks to see if coverage is turned on.

        :return: True if coverage is on, false otherwise.
        """
        do_coverage = self._config.get('Coverage', 'check_coverage', as_object=True, required=False)
        if do_coverage is None:
            do_coverage = False
        return do_coverage

    def civic_coverage_table(self) -> str:
        """
        Gets the name of the table to use for civic coverage queries.

        :return: The name of the table used for civic coverage queries.
        """
        coverage_table = self._config.get('Coverage', 'civic_coverage_table', as_object=False, required=False)
        if coverage_table is None:
            coverage_table = False
        return coverage_table

    def geodetic_coverage_table(self) -> str:
        """
        Gets the name of the table to use for geodetic coverage queries.

        :return: The name of the table used for geodetic coverage queries.
        """
        coverage_table = self._config.get('Coverage', 'geodetic_coverage_table', as_object=False, required=False)
        if coverage_table is None:
            coverage_table = False
        return coverage_table

    def parent_ecrf(self) -> str:
        """
        Gets the parent ECRF if configured.

        """
        parent = self._config.get('Coverage', 'parent_ecrf', as_object=False, required=False)
        if parent is None:
            parent = False
        return parent

    def server_name(self) -> str:
        """
        Gets the current ECRF server name.

        """
        parent = self._config.get('Service', 'source_uri', as_object=False, required=True)
        if parent is None:
            parent = False
        return parent


class CoverageBase(object):
    """
    Base class for anything that will do coverage searches against Postgres.
    """

    __metaclass__ = ABCMeta

    def __init__(self, cov_config: CoverageConfigWrapper, query_executor: civvy_pg.PgQueryExecutor):
        """
        Constructor

        :param cov_config: A reference to the CoverageConfig.
        :param query_executor: An instance of a PgQueryExecutor that will perform the query.
        """
        super().__init__()
        self._config = cov_config
        self._query_executor = query_executor

    @abstractmethod
    def build_coverage_query(self, *args, **kwargs) -> str:
        """
        Abstract method to build the query string to execute. Override this.

        """
        pass

    @abstractmethod
    def build_response(self, result: Iterator[dict]) -> str:
        """
        Abstract method for building the response to the query given the result which will be specific to the
        specific coverage implementation.

        :param result: The result of query execution.
        :return: The coverage response.
        """
        pass

    def execute(self, *args, **kwargs) -> str:
        """
        Executes a civic coverage query.

        """
        query_string: str = self.build_coverage_query(*args, **kwargs)
        query_result = self._query_executor.execute(query_string)
        return self.build_response(query_result)
