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
        self._search_paths = dict()

    def next_path_waypoint(self, path_name='Default'):
        """next_path_waypoint()

        Return the next waypoint in the named path.
        """

        if path_name in self._search_paths:
            if self._search_paths[path_name]:
                return self._search_paths[path_name].pop(0)
            else:
                raise Exception('Path {0} is empty'.format(path_name))
        else:
            raise Exception('Path {0} does not exist'.format(path_name))

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

    def define_search_path(self, path_name='Default', waypoint_list=None):
        """define_search_path()

        Record the ordered waypoints for a named search path.
        """

        self._search_paths[path_name] = list()
        for waypoint in waypoint_list:
            self._search_paths[path_name].append(waypoint)
