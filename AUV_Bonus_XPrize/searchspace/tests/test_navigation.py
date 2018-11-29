"""NavConverter

Tests for the NavConverter class
"""
import pytest


def test_lat_degrees_to_meters():
    """test_lat_degrees_to_meters
    """

    from searchspace.navigation import lat_degrees_to_meters

    assert lat_degrees_to_meters(1.0, 45.0) == pytest.approx(111131.7, rel=0.1)
    assert lat_degrees_to_meters(1.0, 18.0) == pytest.approx(110680.38, rel=0.01)
    assert lat_degrees_to_meters(1.0, 10.0) == pytest.approx(110607.7, rel=0.1)
    assert lat_degrees_to_meters(1.0, 0.0) == pytest.approx(110574.2, rel=0.1)

    ONE_MINUTE = 0.0167
    assert lat_degrees_to_meters(ONE_MINUTE, 0.0) == pytest.approx(1842.90,
                                                                   rel=0.01)

    ONE_SECOND = 0.000278
    assert lat_degrees_to_meters(ONE_SECOND, 0.0) == pytest.approx(30.715,
                                                                   rel=0.001)

def test_lon_degrees_to_meters():
    """test_lon_degrees_to_meters
    """

    from searchspace.navigation import lon_degrees_to_meters

    assert lon_degrees_to_meters(1.0, 45.0) == pytest.approx(78846.8, rel=0.1)
    assert lon_degrees_to_meters(1.0, 30.0) == pytest.approx(96486.2, rel=0.1)
    assert lon_degrees_to_meters(1.0, 0.0) == pytest.approx(111319.491,
                                                            rel=0.001)

    ONE_MINUTE = 0.01667
    assert lon_degrees_to_meters(ONE_MINUTE, 0.0) == pytest.approx(1855.325,
                                                                   rel=0.001)

    ONE_SECOND = 0.000278
    assert lon_degrees_to_meters(ONE_SECOND, 0.0) == pytest.approx(30.922,
                                                                   rel=0.001)
def test_center_calculations():
    """test_center_calculations

    Test the calculations of the boundaries when constructing
    a NavConverter object from a center point.

    http://edwilliams.org/gccalc.htm
    """

    from searchspace.navigation import NavConverter

    nc = NavConverter.construct_from_center(18.45, -66.1,
                                            1000.0, 1000.0)

    assert nc._north_lat == pytest.approx(18.45451, rel=0.00001)
    assert nc._south_lat == pytest.approx(18.44548, rel=0.00001)
    assert nc._east_lon == pytest.approx(-66.09527, rel=0.00001)
    assert nc._west_lon == pytest.approx(-66.10474, rel=0.00001)

    nc = NavConverter.construct_from_center(18.45, -66.1,
                                            3.0, 3.0)

    assert 18.45001 < nc._north_lat < 18.45002
    assert 18.44998 < nc._south_lat < 18.44999
    assert -66.09999 < nc._east_lon < -66.09998
    assert -66.10002 < nc._west_lon < -66.10001

def test_boundary_calculations():
    """test_boundary_calculations

    Test the calculations of the distances when constructing
    a NavConverter object from boundaries.
    """

    from searchspace.navigation import NavConverter

    nc = NavConverter.construct_from_boundaries(30.5,
                                                30.4,
                                                -65.5,
                                                -65.6)

    assert nc._center_lat == 30.45
    assert nc._center_lon == -65.55

    assert nc._east_west_distance_meters == pytest.approx(9604.7, rel=0.1)
    assert nc._north_south_distance_meters == pytest.approx(11086.0, rel=0.1)

def test_geo_to_cartesian():
    """test_geo_to_cartesian()
    """

    from searchspace.navigation import NavConverter
    nc = NavConverter.construct_from_boundaries(30.5,
                                                30.4,
                                                -65.5,
                                                -65.6)

    assert nc._geo_to_cartesian((30.4, -65.6)) == (0.0, 0.0)

    converted_position = nc._geo_to_cartesian((30.5, -65.5))
    calculated_position = (nc._east_west_distance_meters, nc._north_south_distance_meters)
    assert converted_position == calculated_position

def test_cartesian_to_geo():
    """test_cartesian_to_geo()
    """

    from searchspace.navigation import NavConverter
    nc = NavConverter.construct_from_boundaries(30.5,
                                                30.4,
                                                -65.5,
                                                -65.6)

    assert nc._cartesian_to_geo((0.0, 0.0)) == (30.4, -65.6)

    converted_position = nc._cartesian_to_geo((nc._east_west_distance_meters,
                                               nc._north_south_distance_meters))
    assert converted_position[0] == 30.5
    assert -65.39212 < converted_position[1] < -65.39211
