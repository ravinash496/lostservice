#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: lostservice.coverage.resolver
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

Wrapper for coverage resolution operations.
"""


from injector import inject
import lostservice.coverage.base as cov_base
import lostservice.coverage.civic as cov_civic
import lostservice.coverage.geodetic as cov_geo
import lostservice.exception as exp
import lostservice.model.civic as civ_model
import lostservice.model.geodetic as geo_model


class CoverageResolverWrapper(object):
    """
    A class that wraps up coverage resolution and provides methods for both civic and geodetic location types.
    """
    @inject
    def __init__(self,
                 config: cov_base.CoverageConfigWrapper,
                 civic_resolver: cov_civic.CivicCoverageResolver,
                 geodetic_resolver: cov_geo.GeodeticCoverageResolver):
        """
        Constructor

        :param config: Coverage configuration.
        :param civic_resolver: A resolver for civic address locations.
        :param geo_resolver: A resolver for geodetic locations.
        """
        super().__init__()
        self._server_name: str = config.server_name().lower()
        self._do_coverage: bool = config.do_coverage()
        self._civic_resolver = civic_resolver
        self._geodetic_resolver = geodetic_resolver

    def resolve_civic(self, civic_addr: civ_model.CivicAddress) -> str:
        """
        Resolve coverage region for a civic address.

        :param civic_addr: The civic address.
        :return: The authoritative Ecrf server name.
        """
        return self._civic_resolver.execute(civic_addr)

    def resolve_geodetic(self, geometry_model: geo_model.Geodetic2D) -> str:
        """
        Resolve coverage region for a geodetic location.

        :param geometry_model: The geometry model.
        :return: The authoritative Ecrf server name.
        """
        return self._geodetic_resolver.execute(geometry_model)

    def check_coverage(self, model: object) -> str:
        """
        Resolve the coverage region for the given location.

        :param model: The model object with the location, either civic or geodetic.
        :return: The authoritative
        """
        if self._do_coverage:
            source_uri = self._server_name
            authority = ''
            if isinstance(model, civ_model.CivicAddress):
                authority = self.resolve_civic(model)
            else:
                authority = self.resolve_geodetic(model)

            if authority.lower() != self._server_name:
                # if the authority does not match the name of the current server, raise a RedirectException
                raise exp.RedirectException('Server is not authoritative for the given location.', authority)
            else:
                # otherwise return the authority
                return authority
        else:
            # if coverage is turned off, just return the current server name.
            return self._server_name