#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. currentmodule:: lostservice.db.spatial
.. moduleauthor:: Tom Weitzel <tweitzel@geo-comm.com>

Spatial DB functions.
"""
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.sql import select
from shapely.geometry import Point
from geoalchemy2.shape import from_shape

def get_boundary_for_point(engine, table_name, point):

    tbl_metadata = MetaData(bind=engine, schema='public')
    law_table = Table(table_name, tbl_metadata, autoload=True)

    s = select([law_table], law_table.c.wkb_geometry.ST_Contains(point))

    print(s)

    with engine.connect() as conn:
        result = conn.execute(s)

