#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: lostservice.coverage.geodetic
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

Implementation for geodetic coverage resolver.
"""

from injector import inject
from typing import Iterator
import civvy.db.postgis.query as civvy_pg
import lostservice.coverage.base as base
import lostservice.exception as exp
import lostservice.model.geodetic as model


class CivicCoverageResolver(base.CoverageBase):
    """
    Class that implements geodetic coverage resolution

    """

    @inject
    def __init__(self, config: base.CoverageConfigWrapper, query_executor: civvy_pg.PgQueryExecutor):
        """
        Constructor

        :param config: A reference to the CoverageConfig.
        :param query_executor: An instance of a PgQueryExecutor that will perform the query.
        """
        super().__init__(config, query_executor)

    def build_coverage_query(self, geometry_model: model.Geodetic2D) -> str:
        """
        Build the query string for the given geometry.

        :param geometry_model: The geometry model.
        :return: The string to be used to perform the query.
        """
        table_name = self._config.geodetic_coverage_table()
        wkt = geometry_model.to_ogr_geometry().ExportToWkt()

        sql_str = (
            """
            select depth, serviceurn, source, ST_Area(ST_Intersection(ST_GeomFromText('{0}', 4326), wkb_geometry))
            from {0} 
            where ST_Intersects(ST_GeomFromText('{1}', 4326), wkb_geometry)
            order by depth, st_area asc
            """
        )

        return sql_str.format(table_name, wkt)

    def build_response(self, result: Iterator[dict]) -> str:
        """
        Build the response to the query given the result.

        :param result: The result of query execution.
        :return: The coverage response.
        """
        result_list = list(result)
        if result_list:
            # We have a result, and they are already ordered by depth and intersection, so grab the first one.
            authority = result_list[0]
            return authority['lostserver']
        else:
            # There were no results, so we either return the parent, if there is one,
            # or we return a not found exception.
            parent = self._config.parent_ecrf()
            if parent:
                return parent
            else:
                raise exp.NotFoundException('The given address does not match known coverage regions.')
