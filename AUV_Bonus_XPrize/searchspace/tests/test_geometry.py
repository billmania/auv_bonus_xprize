"""Geometry classes and utility functions

"""
import pytest


@pytest.fixture()
def vertex_list():
    from searchspace.geometry import Point

    vertices = list()
    vertices.append(Point(1, 1))
    vertices.append(Point(4, 1))
    vertices.append(Point(4, 5))
    vertices.append(Point(1, 5))

    return vertices


def test_compass_heading_to_polar_angle():
    """test_compass_heading_to_polar_angle
    """

    from math import pi
    from searchspace.geometry import compass_heading_to_polar_angle

    assert compass_heading_to_polar_angle(0) == pytest.approx(pi / 2,
                                                              rel=0.00001)
    assert compass_heading_to_polar_angle(90) == 0.0
    assert compass_heading_to_polar_angle(180) == pytest.approx(3 * pi / 2,
                                                                rel=0.00001)
    assert compass_heading_to_polar_angle(360) == pytest.approx(pi / 2,
                                                                rel=0.00001)
    assert compass_heading_to_polar_angle(270) == pytest.approx(pi,
                                                                rel=0.00001)

def test_formula_from_points():
    """test_formula_from_points
    """

    from searchspace.geometry import formula_from_points, Point

    p1 = Point(0, 0)
    p2 = Point(1, 0)
    slope, y_intercept, x = formula_from_points(p1, p2)
    assert slope == 0
    assert y_intercept == 0
    assert x is None

    p2 = Point(0, 1)
    slope, y_intercept, x = formula_from_points(p1, p2)
    assert slope == float("inf")
    assert y_intercept == 0
    assert x == 0

    p1 = Point(1, 0)
    p2 = Point(1, 0)
    slope, y_intercept, x = formula_from_points(p1, p2)
    assert slope == float("inf")
    assert y_intercept is None
    assert x == 1

    p1 = Point(0, 0)
    p2 = Point(1, 1)
    slope, y_intercept, x = formula_from_points(p1, p2)
    assert slope == 1
    assert y_intercept == 0
    assert x is None

    p1 = Point(0, 0)
    p2 = Point(1, -1)
    slope, y_intercept, x = formula_from_points(p1, p2)
    assert slope == -1
    assert y_intercept == 0
    assert x is None


def test_construct_from_two_points():
    """test_construct_from_two_points
    """

    from searchspace.geometry import Point, Line

    p1 = Point(0, 0)
    p2 = Point(1, 0)
    l = Line.construct_from_two_points(p1, p2)
    assert l.slope == 0
    assert l.y_intercept == 0
    assert l.x is None


def test_construct_from_heading():
    """test_construct_from_heading
    """

    from searchspace.geometry import Point, Line

    p1 = Point(0, 1)
    l = Line.construct_from_heading(p1, 90)
    assert l.slope == 0
    assert l.y_intercept == 1
    assert l.x is None

    l = Line.construct_from_heading(p1, 0)
    assert l.slope == float("inf")
    assert l.y_intercept == 0
    assert l.x is 0

    l = Line.construct_from_heading(p1, 45)
    assert l.slope == pytest.approx(1.0, rel=0.0000001)
    assert l.y_intercept == 1
    assert l.x is None


def test_polygon(vertex_list):
    """test_polygon

    Test the constructor for the Polygon class.
    """

    from searchspace.geometry import Polygon

    rectangle = Polygon(vertex_list)

    assert len(rectangle._vertices) == 4


def test_distance_to_vertices(vertex_list):
    """test_distance_to_vertices
    """

    from searchspace.geometry import Polygon

    rectangle = Polygon(vertex_list)

    assert rectangle._distance_to_vertices(vertex_list[0]) == 12
    assert rectangle._distance_to_vertices(vertex_list[1]) == 12
    assert rectangle._distance_to_vertices(vertex_list[2]) == 12
    assert rectangle._distance_to_vertices(vertex_list[3]) == 12
    assert rectangle._inside_length == 12


def test_point_is_inside(vertex_list):
    """test_point_is_inside
    """

    from searchspace.geometry import Point, Polygon

    inside_pt = Point(3, 4)
    outside_pt = Point(5, 7)
    on_the_edge_pt = Point(4, 3)
    rectangle = Polygon(vertex_list)

    assert rectangle.point_is_inside(inside_pt)
    assert not rectangle.point_is_inside(outside_pt)
    assert rectangle.point_is_inside(on_the_edge_pt)
