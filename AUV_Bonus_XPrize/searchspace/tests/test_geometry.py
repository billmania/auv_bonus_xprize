"""Geometry classes and utility functions

"""
import pytest


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

