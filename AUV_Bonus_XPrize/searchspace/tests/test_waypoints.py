"""SearchSpace waypoints

Tests for the SearchSpace waypoints methods
"""
import pytest


@pytest.fixture()
def waypoint_list():
    """waypoint_list fixture"""

    current_x = 0.0
    current_y = 0.0
    current_depth = 0.0

    waypoint_a = (current_x + 0.0, current_y + 2.0, current_depth + 1.0)
    waypoint_b = (current_x - 2.0, current_y + 2.0, current_depth + 1.0)
    waypoint_c = (current_x - 2.0, current_y - 2.0, current_depth + 1.0)
    waypoint_d = (current_x + 2.0, current_y - 2.0, current_depth + 1.0)
    waypoint_e = (current_x + 2.0, current_y + 2.0, current_depth + 1.0)
    waypoint_origin = (current_x, current_y, current_depth)

    search_path = list()
    search_path.append(waypoint_a)
    search_path.append(waypoint_b)
    search_path.append(waypoint_c)
    search_path.append(waypoint_d)
    search_path.append(waypoint_e)
    search_path.append(waypoint_origin)

    return search_path


def test_inside_the_boundaries(monkeypatch):
    """test_inside_the_boundaries()
    """
    from searchspace.searchspace import SearchSpace
    from searchspace.geometry import Point, Polygon

    s = SearchSpace()
    monkeypatch.setattr(s,
                        '_boundary_polygon',
                        Polygon([Point(10, 300),
                                 Point(100, 300),
                                 Point(100, 100),
                                 Point(10, 100)]))

    inside_pt = Point(80, 150)
    outside_pt = Point(80, 310)
    on_the_edge = Point(99, 150)

    assert s._inside_the_boundaries(inside_pt)
    assert not s._inside_the_boundaries(outside_pt)
    assert s._inside_the_boundaries(on_the_edge)


def test_get_starting_waypt():
    """test_get_starting_waypt()

    """
    from auv_bonus_xprize.settings import config
    from searchspace.searchspace import _starting_waypt

    config['starting']['auv_position_utm'] = '100,300'

    waypt = _starting_waypt()

    assert waypt.x == 100
    assert waypt.y == 300


def test_next_track_heading_and_waypt(monkeypatch):
    """test_next_track_heading_and_waypt

    """

    from searchspace.searchspace import SearchSpace
    from auv_bonus_xprize.settings import config
    from searchspace.geometry import Point, Line, Polygon

    config['starting']['auv_position_utm'] = '80,150'
    config['starting']['northwest_utm'] = '10,300'
    config['starting']['northeast_utm'] = '100,300'
    config['starting']['southeast_utm'] = '100,100'
    config['starting']['southwest_utm'] = '10,100'

    s = SearchSpace()
    monkeypatch.setattr(s,
                        '_boundary_polygon',
                        Polygon([Point(10, 300),
                                 Point(100, 300),
                                 Point(100, 100),
                                 Point(10, 100)]))

    monkeypatch.setattr(s,
                        '_northern_boundary',
                        Line.construct_from_two_points(
                            Point(10, 300),
                            Point(100, 300)))

    monkeypatch.setattr(s,
                        '_eastern_boundary',
                        Line.construct_from_two_points(
                            Point(100, 300),
                            Point(100, 100)))
    monkeypatch.setattr(s,
                        '_southern_boundary',
                        Line.construct_from_two_points(
                            Point(100, 100),
                            Point(10, 100)))
    monkeypatch.setattr(s,
                        '_western_boundary',
                        Line.construct_from_two_points(
                            Point(10, 100),
                            Point(10, 300)))

    monkeypatch.setattr(s, '_current_set', 90)

    heading, waypt = s._next_track_heading_and_waypt(Point(80, 150))
    assert waypt.x == 80 and waypt.y == 300
    assert heading == 0

    monkeypatch.setattr(s, '_current_set', 270)
    heading, waypt = s._next_track_heading_and_waypt(Point(80, 150))
    assert waypt.x == 80 and waypt.y == 300
    assert heading == 0

    monkeypatch.setattr(s, '_current_set', 0)
    heading, waypt = s._next_track_heading_and_waypt(Point(80, 150))
    assert waypt.x == 10 and waypt.y == 150
    assert heading == 270

    monkeypatch.setattr(s, '_current_set', 135)
    heading, waypt = s._next_track_heading_and_waypt(Point(80, 105))
    assert waypt.x == 100 and waypt.y == 125
    assert heading == 45

    monkeypatch.setattr(s, '_current_set', 225)
    heading, waypt = s._next_track_heading_and_waypt(Point(80, 105))
    assert waypt.x == 10 and waypt.y == 175
    assert heading == 315

def test_next_track_depth():
    """test_next_track_depth

    """

    from searchspace.searchspace import _next_track_depth
    from auv_bonus_xprize.settings import config

    config['search']['track_separation_meters'] = '4.5'
    config['search']['min_depth_meters'] = '0.5'
    config['search']['max_depth_meters'] = '30.0'
    assert _next_track_depth(14.0) == 18.5

    config['search']['track_separation_meters'] = '7.0'
    config['search']['max_depth_meters'] = '20.0'
    assert _next_track_depth(14.0) == 20.0

    config['search']['track_separation_meters'] = '-5.0'
    assert _next_track_depth(14.0) == 9.0
