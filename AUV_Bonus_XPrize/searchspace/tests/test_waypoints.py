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


def test_track_is_more_north_south():
    """test_track_is_more_north_south()
    """

    from searchspace.searchspace import SearchSpace
    s = SearchSpace(auv_latitude=0.0,
                    auv_longitude=0.0)

    assert s._track_is_more_north_south(44)
    assert s._track_is_more_north_south(224)
    assert not s._track_is_more_north_south(226)
    assert not s._track_is_more_north_south(46)
    assert s._track_is_more_north_south(0)
    assert s._track_is_more_north_south(360)
    assert s._track_is_more_north_south(180)
    assert not s._track_is_more_north_south(270)


def test_inside_the_boundaries(monkeypatch):
    """test_inside_the_boundaries()
    """
    from searchspace.searchspace import SearchSpace
    s = SearchSpace(auv_latitude=0.0,
                    auv_longitude=0.0)
    monkeypatch.setattr(s, '_northern_limit', 37.5)
    monkeypatch.setattr(s, '_southern_limit', 37.0)
    monkeypatch.setattr(s, '_eastern_limit', -125.0)
    monkeypatch.setattr(s, '_western_limit', -125.5)
    assert s._inside_the_boundaries((37.001, -125.25))

    assert not s._inside_the_boundaries((37.001, -124.0))

    assert not s._inside_the_boundaries((37.6, -125.1))

    assert not s._inside_the_boundaries((37.0, -124.0))


def test_next_track_heading(monkeypatch):
    """test_next_track_heading

    Given the sea current velocity and the current position
    of the AUV, calculate the heading for the next track.
    """

    from searchspace.searchspace import SearchSpace
    s = SearchSpace(auv_latitude=None,
                    auv_longitude=None)
    monkeypatch.setattr(s, '_current_set', 90)
    monkeypatch.setattr(s, '_northern_limit', 37.5)
    monkeypatch.setattr(s, '_southern_limit', 37.0)
    monkeypatch.setattr(s, '_eastern_limit', -125.0)
    monkeypatch.setattr(s, '_western_limit', -125.5)
    assert s._next_track_heading((37.001, -125.25)) == 0

    assert s._next_track_heading((37.2, -125.001)) == 0

    monkeypatch.setattr(s, '_current_set', 10)
    assert s._next_track_heading((37.2, -125.001)) == 280

    monkeypatch.setattr(s, '_current_set', 160)
    assert s._next_track_heading((37.2, -125.001)) == 250

def test_next_waypt():
    """test_next_waypt
    """

    from searchspace.searchspace import SearchSpace
    s = SearchSpace(auv_latitude=None,
                    auv_longitude=None)

    assert False

def test_next_track_depth():
    """test_next_track_depth

    """

    from searchspace.searchspace import SearchSpace
    s = SearchSpace(auv_latitude=None,
                    auv_longitude=None)
    from auv_bonus_xprize.settings import config

    config['search']['track_separation_meters'] = '4.5'
    config['search']['min_depth_meters'] = '0.5'
    config['search']['max_depth_meters'] = '30.0'
    assert s._next_track_depth(14.0) == 18.5

    config['search']['track_separation_meters'] = '7.0'
    config['search']['max_depth_meters'] = '20.0'
    assert s._next_track_depth(14.0) == 20.0

    config['search']['track_separation_meters'] = '-5.0'
    assert s._next_track_depth(14.0) == 9.0


def test_need_gps_fix():
    """test_need_gps_fix

    Based on the time elapsed since the previous GPS fix and the estimate
    of the tracking error, determine if it's necessary to surface in order
    to acquire a GPS fix and adjust the AUV's position.
    """

    assert False


def test_get_gps_fix():
    """test_get_gps_fix

    Move the AUV to the surface and acquire a GPS fix.
    """

    assert False
