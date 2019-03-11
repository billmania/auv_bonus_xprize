#
# Designed and written by:
# Bill Mania
# bill@manialabs.us
#
# under contract to:
# Valley Christian Schools
# San Jose, CA
#
# to compete in the:
# NOAA Bonus XPrize
# January 2019
#
"""SearchSpace module

Tests for the SearchSpace class
"""


def test_class_exists():
    """test_class_exists

    Does the SearchSpace class definition exist.
    """

    from searchspace.searchspace import SearchSpace

    search_space = SearchSpace()

    assert search_space


def test_class_constructor():
    """test_class_constructor

    Are the class instance variables created.
    """

    from searchspace.searchspace import SearchSpace

    search_space = SearchSpace()

    assert isinstance(search_space._cubes, dict)
