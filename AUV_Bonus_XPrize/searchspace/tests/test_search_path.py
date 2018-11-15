"""SearchSpace search path

Tests for the SearchSpace search path methods
"""
import pytest

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

def test_next_path_waypoint(waypoint_list):
    from searchspace.searchspace import SearchSpace
    search_space = SearchSpace()

    search_space.define_search_path(path_name='Path',
                                    waypoint_list=waypoint_list)

    next_waypoint = search_space.next_path_waypoint(path_name='Path')
    assert next_waypoint is waypoint_list[0]

def test_define_search_path(waypoint_list):
    """test_define_search_path()

    Define the waypoints which comprise a search path.
    """
    from searchspace.searchspace import SearchSpace
    search_space = SearchSpace()

    search_space.define_search_path(path_name='Test',
                                    waypoint_list=waypoint_list)

    recorded_waypoint = search_space._search_paths['Test'][1]

    assert recorded_waypoint is waypoint_list[1]
