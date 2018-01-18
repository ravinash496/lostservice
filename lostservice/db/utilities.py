#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. currentmodule:: lostservice.db.utilities
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

General database utility functions
"""

from sqlalchemy import MetaData, Table
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import select, or_
from lostservice.configuration import general_logger
logger = general_logger()
cached_urn_mappings = {}


class MappingDiscoveryException(Exception):
    """
    Raised when something goes wrong in the process of discovering
    the service urn to table mappings.

    :param message: The exception message
    :type message:  ``str``
    :param nested: Nested exception, if any.
    :type nested: 
    """
    def __init__(self, message, nested=None):
        super().__init__(message)
        self._nested = nested


def _get_serviceurn(tablename, engine):
    """
    Gets the service urn from a emergency services boundary table.

    :param tablename: The name of the ESB table
    :type tablename: ``str``
    :param engine: An instance of the database engine.
    :type engine:  :py:class:`sqlalchemy.engine.Engine`
    :return: ``str``
    """
    urn = None
    try:
        result = None
        tbl_metadata = MetaData(bind=engine)
        esb_table = Table(tablename, tbl_metadata, autoload=True)

        q = select([esb_table.c.serviceurn]).distinct()

        with engine.connect() as conn:
            result = conn.execute(q)
            rows = result.fetchall()
            if len(rows) > 1:
                raise MappingDiscoveryException(
                    'Table {0} contained more than one service urn: {1}'.format(tablename, rows))
            urn = rows[0]['serviceurn']
            result.close()
            conn.close()

    except SQLAlchemyError as ex:
        logger.error('Failed to extract mapping for table {0}'.format(tablename), ex)
        raise MappingDiscoveryException('Failed to extract mapping for table {0}'.format(tablename), ex)
    except MappingDiscoveryException as mpe:
        logger.error(mpe)
        raise
    except Exception as ex:
        logger.error(ex)

    return urn


def get_urn_table_mappings(engine):
    """
    Inspects the database and extracts the service urn to table mappings.

    :param engine: An instance of the database engine.
    :type engine:  :py:class:`sqlalchemy.engine.Engine`
    :return: A dictionary containing the service URNs as keys and associated table names as values
    :rtype: ``dict``
    """
    mappings = {}
    try:
        # check in to see if already have service_urn values
        if cached_urn_mappings == {}:
            result = None
            metadata = MetaData(bind=engine, schema='information_schema')
            info_table = Table('tables', metadata, autoload=True)
            s = select([info_table.c.table_name]).where(
                or_(
                    info_table.c.table_name.like('esb%'),
                    info_table.c.table_name.like('aloc%')))

            with engine.connect() as conn:
                result = conn.execute(s)

                for row in result:
                    tablename = row['table_name']
                    urn = _get_serviceurn(tablename, engine)
                    mappings[urn] = tablename
                    cached_urn_mappings[urn] = tablename

                result.close()
                conn.close()

                if not mappings:
                    logger.warning('No service boundary tables were found in the database.')
                    raise MappingDiscoveryException('No service boundary tables were found in the database.')

    except SQLAlchemyError as ex:
        logger.error('Encountered an error when attempting to discover the service boundary tables.', ex)
        raise MappingDiscoveryException(
            'Encountered an error when attempting to discover the service boundary tables.', ex)
    except MappingDiscoveryException as ex:
        logger.error(ex)
        raise

    return cached_urn_mappings
