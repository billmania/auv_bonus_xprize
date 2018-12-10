"""SearchSpace module

Tests for the SearchSpace class
"""


def test_class_exists():
    """test_class_exists

    Does the SearchSpace class definition exist.
    """

    from searchspace.searchspace import SearchSpace

    search_space = SearchSpace(0, 0)

    assert search_space


def test_class_constructor():
    """test_class_constructor

    Are the class instance variables created.
    """

    from searchspace.searchspace import SearchSpace

    search_space = SearchSpace(0, 0)

    assert isinstance(search_space._cubes, dict)
    assert isinstance(search_space._plume_source, tuple)
