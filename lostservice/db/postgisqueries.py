from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.sql import select, or_
from shapely.geometry import Point
from shapely.geometry.polygon import LinearRing
from shapely.wkt import loads
from geoalchemy2.shape import from_shape
from osgeo import osr
from osgeo import ogr


def get_boundary_for_geom(engine, table_name, geom):
    """
    Queries the given table for the boundary in which the givne
    geometry falls.

    :param engine: SQLAlchemy database engine
    :param table_name: The name of the service boundary table.
    :param geom: The geometry to use in the search as a GeoAlchemy WKBElement.
    :return: Nothing, prints out results along the way.
    """
    # Get a reference to the table we're going to look in.
    tbl_metadata = MetaData(bind=engine)
    the_table = Table(table_name, tbl_metadata, autoload=True)

    # Construct the "contains" query.
    s = select([the_table], the_table.c.wkb_geometry.ST_Contains(geom))

    # Print the query just to see what it looks like.
    print(s)

    # Connect to the database and execute the query.
    with engine.connect() as conn:
        result = conn.execute(s)

        for row in result:
            print(row)

    # Construct the "intersection" query.
    s2 = select([the_table.c.displayname, the_table.c.serviceurn, the_table.c.routeuri, the_table.c.servicenum], the_table.c.wkb_geometry.ST_Intersects(geom))

    # Print the query just to see what it looks like.
    print(s2)

    # Connect to the database and execute the query.
    with engine.connect() as conn:
        result = conn.execute(s2)

    return result

def query_for_point(x, y, srid, boundary_table, engine):
    """
    Executes a query for a point.

    :param x: The x coordinate of the point.
    :param y: The y coordinate of the point.
    :param srid: The spatial reference Id of the point.
    :param boundary_table: The name of the service boundary table.
    :param engine: SQLAlchemy database engine.
    :return: Nothing.
    """
    # Create a Shapely Point
    pt = Point(x, y)
    # Get a GeoAlchemy WKBElement from the point.
    wkb_pt = from_shape(pt, srid)
    # Run the query.
    get_boundary_for_geom(engine, boundary_table, wkb_pt)


def query_for_circle(x, y, srid, radius, uom, boundary_table, engine):
    """
    Executes a query for a circle.

    :param x: The x coordinate of the center.
    :param y: The y coordinate of the center.
    :param srid: The spatial reference id of the center point.
    :param radius: The radius of the circle.
    :param uom: The unit of measure of the radius.
    :param boundary_table: The name of the service boundary table.
    :param engine: SQLAlchemy database engine.
    :return: Nothing.
    """

    # Source spatial reference.
    source = osr.SpatialReference()
    source.ImportFromEPSG(srid)

    # The target will depend on the value of uom, but we'll just assume
    # it's 9001/meters for now and project to 3857.
    target = osr.SpatialReference()
    target.ImportFromEPSG(3857)

    # Set up the transform.
    transform = osr.CoordinateTransformation(source, target)

    # Create a geometry we can use with the transform.
    center = ogr.CreateGeometryFromWkt('POINT({0} {1})'.format(x, y))

    # Transform it and apply the buffer.
    center.Transform(transform)
    circle = center.Buffer(radius)

    # Now transform it back and extract the wkt
    reverse_transform = osr.CoordinateTransformation(target, source)
    circle.Transform(reverse_transform)
    wkt_circle = circle.ExportToWkt()

    # load up a new Shapely Polygon from the WKT and convert it to a GeoAlchemy2 WKBElement
    # that we can use to query.
    poly = loads(wkt_circle)
    wkb_circle = from_shape(poly, srid)

    # Now execute the query.
    result = get_boundary_for_geom(engine, boundary_table, wkb_circle)
    return result

def query_for_polygon(points, srid, boundary_table, engine):
    """
    Executes a query for a polygon.

    :param points: A list of vertices in (x,y) format.
    :param srid: The spatial reference Id of the vertices.
    :param boundary_table: The name of the service boundary table.
    :param engine: SQLAlchemy database engine.
    :return: Nothing
    """
    ring = LinearRing(points)
    wkb_ring = from_shape(ring, srid)
    get_boundary_for_geom(engine, boundary_table, wkb_ring)


if __name__ == '__main__':
    db_engine = create_engine('postgresql://postgres:Today123!@localhost:5432/sr')

    # Point
    query_for_point(-68.8456886863956, 44.8718852087561, 4326, 'esblaw', db_engine)

    # Circle
    # UOM = urn:ogc:def:uom:EPSG::9001 which is meters
    query_for_circle(-68.4977255651657, 45.4430670070877, 4326, 6105.41237061098, 9001, 'esblaw', db_engine)

    # Polygon
    vertices = [
        (-68.9794553026202, 45.4209978589603),
        (-69.0051247132027, 45.4173275783646),
        (-69.0041739942923, 45.4171607417598),
        (-68.9804060215307, 45.4118217101367),
        (-68.9794553026202, 45.4209978589603)]

    query_for_polygon(vertices, 4326, 'esblaw', db_engine)
