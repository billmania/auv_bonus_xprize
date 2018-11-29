"""SearchSpace

The functionality for the search space in which the AUV
operates.
"""

from auv_bonus_xprize.settings import config
from searchspace.navigation import NavConverter


class SearchSpace(object):
    """SearchSpace - The representation of the SearchSpace.

    """
    def __init__(self,
                 auv_latitude,
                 auv_longitude):
        """__init__() - Create an instance of the SearchSpace
        """
        self._cubes = dict()
        self._plume_source = (None, None)
        self._auv_latitude = auv_latitude
        self._auv_longitude = auv_longitude
        self._auv_depth = 0.0
        self._search_paths = dict()
        self.set_current_velocity(0, 0.0)

        self._northern_limit = None
        self._southern_limit = None
        self._eastern_limit = None
        self._western_limit = None

    def _track_is_more_north_south(self, proposed_heading):
        """track_is_more_north_south()

        Return True if the proposed_heading is aligned more
        north and south.
        """

        heading = proposed_heading % 360
        if 135 <= heading < 225:
            return True
        elif 315 <= heading or heading < 45:
            return True
        else:
            return False

    def _next_track_depth(self, track_depth):
        """next_track_depth()

        Calculate the depth for a new track, based on the current
        depth and the configuration parameters.
        """

        min_depth = float(config['search']['min_depth_meters'])
        max_depth = float(config['search']['max_depth_meters'])
        vertical_separation = float(
            config['search']['track_separation_meters']
        )
        new_depth = track_depth + vertical_separation
        if new_depth < min_depth:
            return min_depth
        elif new_depth > max_depth:
            return max_depth

        return new_depth

    def _next_track_heading(self, starting_waypt):
        """next_track_heading()

        Given the sea current velocity and the starting_waypt,
        calculate the heading for the next track.
        """

        starting_lat = starting_waypt[0]
        starting_lon = starting_waypt[1]

        track_heading = (self._current_set + 90) % 360
        if self._inside_the_boundaries(starting_waypt):
            if self._track_is_more_north_south(track_heading):
                degrees_to_north = self._northern_limit - starting_lat
                if degrees_to_north <= (self._northern_limit -
                                        self._southern_limit) / 2.0:
                    if 90 < track_heading < 270:
                        return track_heading
            else:
                degrees_to_east = self._eastern_limit -starting_lon 
                if degrees_to_east <= (self._eastern_limit -
                                       self._western_limit) / 2.0:
                    if 180 <= track_heading < 360:
                        return track_heading

        else:
            raise Exception('Starting point is outside the boundaries')

        return (track_heading + 180) % 360

    def _inside_the_boundaries(self, waypt):
        """_inside_the_boundaries()

        Return True if the waypt is inside the
        bounded search area.
        """

        latitude = waypt[0]
        longitude = waypt[1]
        if self._northern_limit > latitude  > self._southern_limit:
            if self._eastern_limit > longitude > self._western_limit:
                return True
            else:
                return False
        else:
            return False

    def _next_waypt(self, starting_waypt, bearing_to_next_waypt):
        """_next_waypt()

        Calculate the waypoint which is at the given bearing
        from the starting_waypt and as close to the relevant
        boundary as the configuration parameters allow.
        """
        waypt = (0.0, 0.0)

        bearing = bearing_to_next_waypt % 360
        boundary_buffer = config['search']['boundary_buffer_meters']

        if bearing == 0:
            #
            # add the distance from the starting_waypt to the north
            # buffer to the starting_waypt lat.
            #
            pass
        elif bearing < 90:
            #
            # add the distance from the starting_waypt to the east
            # buffer to the starting_waypt lon. then add
            # tan(bearing)A to the lat.
            # 
            pass
        elif bearing == 90:
            #
            # add the distance from the starting_waypt to the east
            # buffer to the starting_waypt lon.
            #
            pass
        elif bearing < 180:
            #
            # subtract the distance from the starting_waypt to the
            # south buffer from the starting_waypt lat. then add
            # tan(bearing)A to the lon.
            #
            pass
        elif bearing == 180:
            #
            # subtract the distance from the starting_waypt to the
            # south buffer from the starting_waypt lat.
            #
            pass
        elif bearing < 270:
            #
            # subtract the distance from the starting_waypt to the
            # west buffer from the starting_waypt lon. then subtract
            # tan(bearing)A from the lat.
            #
            pass
        elif bearing == 270:
            #
            # subtract the distance from the starting_waypt to the
            # west buffer from the starting_waypt lon.
            #
            pass
        else:
            #
            # add the distance from the starting_waypt to the north
            # buffer to the starting_waypt lat. then  ...
            #
            pass

        # find the point which is on the boundary buffer
        # use TOA to find the next waypt

        return waypt

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

    def set_current_velocity(self, current_set, current_drift):
        """set_current_velocity()
        """

        if 0 <= current_set < 360:
            self._current_set = current_set,
        else:
            raise Exception('current_set must be a compass heading in degrees')
        if current_drift >= 0.0:
            self._current_drift = current_drift
        else:
            raise Exception('current_drift must be non-negative knots')

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

        self.nav_converter = NavConverter.construct_from_boundaries(
            self._northern_limit,
            self._southern_limit,
            self._eastern_limit,
            self._western_limit)

    def calculate_search_path(self):
        """calculate_search_path()

        Using the current position of AUV as a starting point
        and the set and drift of the current, calculate an ordered
        list of waypoints for the AUV to follow.
        """

        max_depth = config['search']['max_depth_meters']
        track_separation = config['search']['track_separation_meters']
        track_passes = int(max_depth / track_separation)

        track_heading = self._next_track_heading(
            (self._auv_latitude, self._auv_longitude))
        track_depth = self._auv_depth

        waypt = (self._auv_latitude, self._auv_longitude, self._auv_depth)
        waypt_list = list()

        while track_passes:
            waypt = self._next_waypt(waypt, track_heading)
            waypt_list.append(waypt + (track_depth,))

            track_depth = self._next_track_depth(track_depth)
            waypt_list.append(waypt + (track_depth,))

            track_heading = self._next_track_heading(waypt)

            track_passes = track_passes - 1

        return waypt_list

    def define_search_path(self, path_name='Default', waypoint_list=None):
        """define_search_path()

        Record the ordered waypoints for a named search path.
        """

        self._search_paths[path_name] = list()
        for waypoint in waypoint_list:
            self._search_paths[path_name].append(waypoint)

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
