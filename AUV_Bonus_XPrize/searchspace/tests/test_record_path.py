"""SearchSpace AUV path

Tests for the SearchSpace AUV path methods
"""

import pytest
from auv_bonus_xprize.settings import config

def test_record_auv_path():
    """test_record_auv_path

    Does the function update the search space.
    """

    from searchspace.searchspace import SearchSpace
    search_space = SearchSpace(0, 0)

    path_x = 13.1
    path_y = 12.0
    path_depth = 14.5
    sensor_value = 4
    sensor_gain = 10

    assert len(search_space._cubes) == 0

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
    search_space = SearchSpace(0, 0)

    northern_latitude = 14.654
    southern_latitude = 14.65
    eastern_longitude = -32.1
    western_longitude = -32.12
    depth = 14.0

    boundary_buffer = 10.0
    config['search']['boundary_buffer_meters'] = str(boundary_buffer)

    search_space.set_search_boundaries(
        northern_latitude,
        southern_latitude,
        eastern_longitude,
        western_longitude,
        depth)

    assert search_space._max_depth == depth
    assert search_space._southern_boundary.y_intercept == boundary_buffer

def test_set_search_boundaries_exception():
    """test_set_search_boundaries_exception

    Verify bad boundaries cause an exception.
    """

    from searchspace.searchspace import SearchSpace
    search_space = SearchSpace(0, 0)

    northern_latitude = 14.654
    southern_latitude = 14.7
    eastern_longitude = -32.1
    western_longitude = -32.12
    depth = 14.0

    with pytest.raises(ValueError) as exc_info:
        search_space.set_search_boundaries(
            northern_latitude,
            southern_latitude,
            eastern_longitude,
            western_longitude,
            depth)

    exc_msg = exc_info.value.args[0]
    assert exc_msg == 'North and south boundaries illogical'