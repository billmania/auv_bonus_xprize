"""SearchSpace

The functionality for the search space in which the AUV
operates.
"""

from math import atan2, isclose

from auv_bonus_xprize.settings import config
from searchspace.geometry import Point, Line, Polygon
from searchspace.geometry import points_distance
from searchspace.geometry import compass_heading_to_polar_angle


def _next_track_depth(present_depth):
    """next_track_depth()

    Calculate the depth for a new track, based on the present
    depth and the configuration parameters.
    """

    min_depth = float(config['search']['min_depth_meters'])
    max_depth = float(config['search']['max_depth_meters'])
    vertical_separation = float(
        config['search']['track_separation_meters']
    )
    new_depth = present_depth + vertical_separation
    if new_depth < min_depth:
        return min_depth
    elif new_depth > max_depth:
        return max_depth

    return new_depth


def _starting_waypt():
    """_starting_waypt()

    Retrieve the starting position UTM coordinates from
    the config file and return the position as a Point.
    """

    auv_position = config['starting']['auv_position_utm'].split(',')
    return Point(int(float(auv_position[0])),
                 int(float(auv_position[1])))


class SearchSpace(object):
    """SearchSpace - The representation of the SearchSpace.

    """
    def __init__(self):
        """__init__() - Create an instance of the SearchSpace
        """
        self._cubes = dict()

        self._boundary_polygon = None
        self._northern_boundary = None
        self._southern_boundary = None
        self._eastern_boundary = None
        self._western_boundary = None
        self._perimeter_length = None

        self._current_set = 0
        self._current_drift = 0.0

    def _next_track_heading_and_waypt(self, starting_waypt):
        """next_track_heading_and_waypt()

        Given the sea current velocity and the starting_waypt,
        calculate the heading for the next track.

        Determine the distance to each boundary. Return the heading
        which is perpendicular to the current set and a waypt
        which intersects the boundary on that heading.
        """

        if self._inside_the_boundaries(starting_waypt):

            track_heading = (self._current_set + 90) % 360

            track_line = Line.construct_from_heading(starting_waypt,
                                                     track_heading)

            distances = list()
            for boundary in [self._northern_boundary,
                             self._eastern_boundary,
                             self._southern_boundary,
                             self._western_boundary]:
                intersect_pt = boundary.find_intersection(track_line)
                if intersect_pt:
                    distance_to_boundary = points_distance(starting_waypt,
                                                           intersect_pt)
                    distances.append((distance_to_boundary,
                                      intersect_pt))
            distances.sort()

            for intersect_pt_idx in range(1, len(distances)):
                intersect_pt = distances[intersect_pt_idx][1]
                if not self._inside_the_boundaries(intersect_pt):
                    continue

                angle_to_intersect_pt = atan2(
                    intersect_pt.y - starting_waypt.y,
                    intersect_pt.x - starting_waypt.x)

                if not isclose(angle_to_intersect_pt,
                               compass_heading_to_polar_angle(
                                   track_heading),
                               rel_tol=1e-5):
                    track_heading = (track_heading + 180) % 360

                return track_heading, intersect_pt

            raise Exception('No waypoint is inside the boundaries')
        else:
            raise Exception('Starting point is outside the boundaries')

    def _inside_the_boundaries(self, waypt):
        """_inside_the_boundaries()

        Return True if the waypt is inside the
        bounded search area.
        """

        return self._boundary_polygon.point_is_inside(waypt)

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

    def set_current_velocity(self):
        """set_current_velocity()
        """

        current_set = int(float(config['starting']['set']))
        current_drift = float(config['starting']['drift'])
        if 0 <= current_set < 360:
            self._current_set = current_set
        else:
            raise Exception('current_set must be a compass heading in degrees')
        if current_drift >= 0.0:
            self._current_drift = current_drift
        else:
            raise Exception('current_drift must be non-negative knots')

    def set_search_boundaries(self):
        """set_search_boundaries

        Calculate the horizontal search boundaries as lines offset
        from the configured contest boundaries by a buffer. The
        definition of the contest area vertices, as well as the
        buffer at the boundary, come from the configuration file.

        The results of this method are saved as instance variables
        named like _northern_boundary and are lines defined to
        work with UTM positions.

        https://www.latlong.net/lat-long-utm.html

        https://stackoverflow.com/questions/343865/how-to-convert-from-utm-to-latlng-in-python-or-javascript
        """

        boundary_buffer = float(config['search']['boundary_buffer_meters'])

        vertex_list = list()

        northwest_utm = config['starting']['northwest_utm'].split(',')
        northwest_vertex = Point(int(northwest_utm[0]) + boundary_buffer,
                                 int(northwest_utm[1]) - boundary_buffer)
        vertex_list.append(northwest_vertex)

        northeast_utm = config['starting']['northeast_utm'].split(',')
        northeast_vertex = Point(int(northeast_utm[0]) - boundary_buffer,
                                 int(northeast_utm[1]) - boundary_buffer)
        vertex_list.append(northeast_vertex)

        southeast_utm = config['starting']['southeast_utm'].split(',')
        southeast_vertex = Point(int(southeast_utm[0]) - boundary_buffer,
                                 int(southeast_utm[1]) + boundary_buffer)
        vertex_list.append(southeast_vertex)

        southwest_utm = config['starting']['southwest_utm'].split(',')
        southwest_vertex = Point(int(southwest_utm[0]) + boundary_buffer,
                                 int(southwest_utm[1]) + boundary_buffer)
        vertex_list.append(southwest_vertex)

        self._boundary_polygon = Polygon(vertex_list)

        self._northern_boundary = Line.construct_from_two_points(
            northwest_vertex,
            northeast_vertex)
        self._perimeter_length = points_distance(
            northwest_vertex,
            northeast_vertex)

        self._eastern_boundary = Line.construct_from_two_points(
            northeast_vertex,
            southeast_vertex)
        self._perimeter_length += points_distance(
            northeast_vertex,
            southeast_vertex)

        self._southern_boundary = Line.construct_from_two_points(
            southeast_vertex,
            southwest_vertex)
        self._perimeter_length += points_distance(
            southeast_vertex,
            southwest_vertex)

        self._western_boundary = Line.construct_from_two_points(
            southwest_vertex,
            northwest_vertex)
        self._perimeter_length += points_distance(
            southwest_vertex,
            northwest_vertex)

    def calculate_search_path(self):
        """calculate_search_path()

        Using the current position of AUV as a starting point
        and the set and drift of the current, calculate an ordered
        list of waypoints for the AUV to follow.
        """

        min_depth = float(config['search']['min_depth_meters'])
        max_depth = float(config['search']['max_depth_meters'])
        track_separation = float(config['search']['track_separation_meters'])
        track_passes = int((max_depth - min_depth) / track_separation) + 1

        track_depth = min_depth

        self.set_current_velocity()

        heading, waypt = self._next_track_heading_and_waypt(
            _starting_waypt())
        search_path = list()
        search_path.append(waypt.as_tuple() + (track_depth, heading))

        while track_passes:
            heading, waypt = self._next_track_heading_and_waypt(waypt)
            search_path.append(waypt.as_tuple() + (track_depth, heading))

            if track_passes > 1:
                track_depth = _next_track_depth(track_depth)
                search_path.append(waypt.as_tuple() + (track_depth, None))

            track_passes = track_passes - 1

        return search_path
