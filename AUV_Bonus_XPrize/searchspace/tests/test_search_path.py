"""SearchSpace search path

Tests for the SearchSpace search path methods
"""


def test_func_exists():
    """test_func_exists

    Does the SearchSpace.next_search_waypoint method definition exist.
    """

    from searchspace.searchspace import SearchSpace
    search_space = SearchSpace()

    assert search_space.next_search_waypoint


def test_waypoint_parameters():
    """test_waypoint_parameters

    Does the function return the expected number and type of
    waypoint parameters.
    """

    from searchspace.searchspace import SearchSpace
    search_space = SearchSpace()

    (waypoint_x,
     waypoint_y,
     waypoint_depth) = search_space.next_search_waypoint()

    assert isinstance(waypoint_x, float)
    assert isinstance(waypoint_y, float)
    assert isinstance(waypoint_depth, float)
