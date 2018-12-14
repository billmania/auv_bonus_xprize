"""navigation utility class

"""
from math import cos, radians
from auv_bonus_xprize.settings import config
from searchspace.geometry import Point, Line, Polygon


class NavConverter(object):
    """NavConverter

    Methods to convert between geographic coordinates
    and Cartesian coordinates.
    """

    @classmethod
    def construct_from_center(cls,
                              center_lat,
                              center_lon,
                              east_west_distance,
                              north_south_distance):
        """construct_from_center()

        Create an instance of the class centered at the
        given position and with the given dimensions.
        """
        instance = cls()

        instance._constructor = 'center'

        instance._center_lat = center_lat
        instance._center_lon = center_lon
        instance._east_west_distance_meters = east_west_distance
        instance._north_south_distance_meters = north_south_distance

        deg_per_m = (1.0 / lon_degrees_to_meters(1.0,
                                                 instance._center_lat))
        distance_in_deg = instance._east_west_distance_meters * deg_per_m
        instance._east_lon = instance._center_lon + (distance_in_deg / 2.0)
        instance._west_lon = instance._center_lon - (distance_in_deg / 2.0)

        deg_per_m = (1.0 / lat_degrees_to_meters(1.0,
                                                 instance._center_lat))
        distance_in_deg = instance._north_south_distance_meters * deg_per_m
        instance._north_lat = instance._center_lat + (distance_in_deg / 2.0)
        instance._south_lat = instance._center_lat - (distance_in_deg / 2.0)

        return instance

    @classmethod
    def construct_from_boundaries(cls,
                                  north_lat,
                                  south_lat,
                                  east_lon,
                                  west_lon):
        """construct_from_boundaries()

        Create an instance of the class based on the given
        boundaries.
        """

        if north_lat < south_lat or east_lon < west_lon:
            raise Exception('North must be greater than south and east must be greater than west')

        instance = cls()

        instance._constructor = 'boundaries'

        instance._north_lat = north_lat
        instance._south_lat = south_lat
        instance._east_lon = east_lon
        instance._west_lon = west_lon

        instance._center_lat = (north_lat - south_lat) / 2.0 + south_lat
        instance._center_lon = (east_lon - west_lon) / 2.0 + west_lon
        instance._east_west_distance_meters = lon_degrees_to_meters(east_lon - west_lon,
                                                                    instance._center_lat)
        instance._north_south_distance_meters = lat_degrees_to_meters(north_lat - south_lat,
                                                                      instance._center_lat)

        return instance

    def geo_to_cartesian(self, geo_position):
        """geo_to_cartesian()

        Convert the lat and lon from position to x and y
        in the local area. Cartesian (0, 0) is equivalent
        to Geo (_west_lon, _south_lat).
        """

        lat = geo_position[0]
        lon = geo_position[1]
        if (lat < self._south_lat or
            lat > self._north_lat or
            lon < self._west_lon or
            lon > self._east_lon):

            raise Exception('Position is outside the defined area.')

        x = lon_degrees_to_meters(lon - self._west_lon, self._center_lat)
        y = lat_degrees_to_meters(lat - self._south_lat, self._center_lat)

        return Point(x, y)

    def cartesian_to_geo(self, cartesian_position):
        """cartesian_to_geo()

        Convert the x and y from cartesian_position to lat
        and lon. Geo (_west_lon, _south_lat) is equivalent to
        Cartesian (0, 0).
        """

        x = cartesian_position[0]
        y = cartesian_position[1]
        if (x < 0.0 or
            x > self._east_west_distance_meters or
            y < 0.0 or
            y > self._north_south_distance_meters):

            raise Exception('Position is outside the defined area.')

        lat = self._south_lat + y * (1 / lat_degrees_to_meters(1.0,
                                                               abs(self._center_lat)))
        lon = self._west_lon + x * (1 / lon_degrees_to_meters(1.0,
                                                              abs(self._center_lon)))

        return (lat, lon)


def lat_degrees_to_meters(lat_degrees, at_this_latitude):
    """lat_degrees_to_meters()

    Convert the decimal latitude degrees argument to meters,
    at the given latitude.

    http://www.csgnetwork.com/degreelenllavcalc.html
    """

    if (lat_degrees > 10.0 or
        lat_degrees < 0.0 or
        at_this_latitude > 90.0 or
        at_this_latitude < 0.0):

        raise Exception('Degrees must be [0.0, 10.0]. Latitude must be [0.0, 90.0]')

    lat_in_rads = radians(abs(at_this_latitude))

    second = 559.82 * cos(2 * lat_in_rads)
    fourth = 1.175 * cos(4 * lat_in_rads)
    sixth = 0.0023 * cos(6 * lat_in_rads)

    meters_per_degree = 111132.92 - second + fourth - sixth

    return lat_degrees * meters_per_degree


def lon_degrees_to_meters(lon_degrees, at_this_latitude):
    """lon_degrees_to_meters()

    Convert the decimal longitude degrees argument to meters,
    at the given latitude.
    """

    if (lon_degrees > 10.0 or
        lon_degrees < 0.0 or
        at_this_latitude >= 90.0 or
        at_this_latitude < 0.0):

        raise Exception('Degrees must be [0.0, 10.0]. Latitude must be [0.0, 90.0)')

    lat_in_rads = radians(abs(at_this_latitude))

    first = 111412.84 * cos(lat_in_rads)
    third = 93.5 * cos(3 * lat_in_rads)
    fifth = 0.118 * cos(5 * lat_in_rads)
    meters_per_degree = first - third + fifth

    return lon_degrees * meters_per_degree
