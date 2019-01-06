"""SearchSpace search path

Tests for the SearchSpace search path methods
"""
import pytest


@pytest.fixture
def boundary_vertices():
    """boundary_vertices

    Fixture to provide search boundary vertices.
    """

    from searchspace.geometry import Point

    boundary_vertices = list()
    boundary_vertices.append(Point(18.1, -37.1))
    boundary_vertices.append(Point(18.1, -37.0))
    boundary_vertices.append(Point(18.0, -37.0))
    boundary_vertices.append(Point(18.0, -37.1))

    return boundary_vertices


@pytest.fixture()
def waypoint_list():
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


def test_record_auv_path():
    """test_record_auv_path

    Does the function update the search space.
    """

    from searchspace.searchspace import SearchSpace
    search_space = SearchSpace()

    path_x = 13.1
    path_y = 12.0
    path_depth = 14.5
    sensor_value = 4
    sensor_gain = 10

    assert not search_space._cubes

    search_space.record_auv_path(
        path_x,
        path_y,
        path_depth,
        sensor_value,
        sensor_gain)

    assert len(search_space._cubes) == 1
    assert (path_x, path_y, path_depth) in search_space._cubes


def test_set_search_boundaries():
    """test_set_search_boundaries

    Set the boundaries of the search space.
    """

    from searchspace.searchspace import SearchSpace
    from auv_bonus_xprize.settings import config

    search_space = SearchSpace()

    boundary_buffer = 10.0
    depth = 14.0

    config['search']['boundary_buffer_meters'] = str(boundary_buffer)
    config['starting']['northwest_utm'] = '602978,4127097'
    config['starting']['northeast_utm'] = '603978,4127097'
    config['starting']['southeast_utm'] = '603978,4126097'
    config['starting']['southwest_utm'] = '602978,4126097'
    config['search']['max_depth_meters'] = str(depth)

    search_space.set_search_boundaries()

    assert search_space._perimeter_length > 0
    assert search_space._perimeter_length == 3920
