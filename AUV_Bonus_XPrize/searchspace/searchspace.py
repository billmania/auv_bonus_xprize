"""SearchSpace

The functionality for the search space in which the AUV
operates.
"""


class SearchSpace(object):
    """SearchSpace - The representation of the SearchSpace.

    """
    def __init__(self):
        """__init__() - Create an instance of the SearchSpace
        """
        self._cubes = dict()
        self._plume_source = tuple()

    def next_search_waypoint(self):
        """next_search_waypoint()

        Return the next waypoint in the current search path.
        """

        waypoint_x = 0.0
        waypoint_y = 0.0
        waypoint_depth = 0.0

        return waypoint_y, waypoint_x, waypoint_depth

    def record_auv_path(
        self,
        auv_x,
        auv_y,
        auv_depth,
        sensor_value,
        sensor_gain
    ):
        """record_auv_path()

        Update the measurements for a particular cell visited
        by the AUV.
        """

        self._cubes[(auv_x, auv_y, auv_depth)] = (sensor_value, sensor_gain)

    def set_search_boundaries(
        self,
        northern_latitude,
        southern_latitude,
        eastern_longitude,
        western_longitude,
        depth
    ):
        """set_search_boundaries

        Record the horizontal and depth boundaries of the search
        space.
        """

        self._northern_limit = northern_latitude
        self._southern_limit = southern_latitude
        self._eastern_limit = eastern_longitude
        self._western_limit = western_longitude
        self._max_depth = depth

        if self._northern_limit <= self._southern_limit:
            raise ValueError('North and south boundaries illogical')

        if self._eastern_limit <= self._western_limit:
            raise ValueError('East and west boundaries illogical')

        if self._max_depth <= 0.0:
            raise ValueError('Depth boundary is not in the water')

