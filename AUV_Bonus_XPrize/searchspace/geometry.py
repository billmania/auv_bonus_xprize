"""Geometry

Classes and methods for representing and interacting with
points, lines, and polygons.
"""

from math import sqrt, radians, cos, sin, pi
from math import atan, degrees
import matplotlib.path as mplPath

INFINITE = float("inf")


def bearing_to_point(point1, point2):
    """bearing_to_point()

    Return the compass heading in degrees from
    point1 to point2. If the two input points are
    the same point, return None.
    """

    if point1 == point2:
        return None

    if point1.x == point2.x:
        if point2.y > point1.y:
            return 0
        else:
            return 180

    if point1.y == point2.y:
        if point2.x > point1.x:
            return 90
        else:
            return 270

    slope = float(point2.y - point1.y) / (point2.x - point1.x)
    if slope > 0:
        bearing = int(90 - degrees(atan(slope)))
        if point2.y < point1.y:
            bearing = (bearing + 180) % 360
    else:
        bearing = int(-1 * degrees(atan(slope)) + 90)
        if point2.y > point1.y:
            bearing = (bearing + 180) % 360

    return bearing


def points_distance(point1, point2):
    """distance

    Calculate the Euclidean distance between point1 and point2.
    """

    if point1 == point2:
        return 0.0

    return sqrt((point1.x - point2.x) ** 2 +
                (point1.y - point2.y) ** 2)


def compass_heading_to_polar_angle(heading):
    """compass_heading_to_polar_angle()

    Convert a compass heading in degrees to a polar angle
    in radians. The heading is [0, 360), with 0 being north
    and the heading value increasing from the north to the
    east.

    The polar angle will be [0, 2*pi), with 0 being east
    and the angle value increasing from the east to the north.
    """

    compass_heading = int(heading) % 360
    angle = radians((-1 * (compass_heading - 360) + 90) % 360)

    if angle > pi:
        return angle - 2 * pi
    else:
        return angle


def formula_from_points(p1, p2):
    """formula_from_points()

    Given two points on a line, return the slope, y_intercept,
    and x.
    """

    if p1.x == p2.x:
        x = p1.x
        slope = INFINITE
        if x == 0:
            y_intercept = 0
        else:
            y_intercept = None
    else:
        slope = float(p2.y - p1.y) / float(p2.x - p1.x)
        y_intercept = -1 * slope * p2.x + p2.y
        x = None

    return slope, y_intercept, x


class Point(object):
    """Point

    Represent a two-dimensional point and its
    properties.
    """

    def __init__(self, x=0, y=0):
        """__init__

        Record the dimensions of a point.
        """

        self.x = x
        self.y = y

        self.dimensions = 2

        if self.x >= 0:
            if self.y >= 0:
                self.quadrant = 'I'
            else:
                self.quadrant = 'IV'

        else:
            if self.y >= 0:
                self.quadrant = 'II'
            else:
                self.quadrant = 'III'

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.x == other.x and self.y == other.y
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def as_tuple(self):
        """as_tuple()

        Return the Point coordinates as a tuple.
        """

        return (self.x, self.y)

    def __repr__(self):
        """__repr__ Formatted output of the point dimensions."""

        return '(%f, %f)' % (self.x, self.y)


class Line(object):
    """Line

    Represent a line and its properties. The line can be
    initially described with either two points or with
    a slope and a y-intercept.
    """

    @classmethod
    def construct_from_two_points(cls, p1, p2):
        """construct_from_two_points

        Instantiate a Line based on two points on that line.
        """

        instance = cls()

        instance.slope, instance.y_intercept, instance.x = formula_from_points(
            p1,
            p2)

        return instance

    @classmethod
    def construct_from_formula(cls, slope, y_intercept, x):
        """construct_from_formula

        Instantiate a Line based on its formula.
        """

        instance = cls()

        instance.slope = slope
        instance.y_intercept = y_intercept
        if slope is INFINITE:
            if y_intercept is not None:
                instance.x = 0
            elif x is not None:
                instance.x = x
            else:
                raise Exception('Not enough information to define a line.')

        elif y_intercept is not None:
            instance.x = None

        else:
            raise Exception('Not enough information to define a line.')

        return instance

    @classmethod
    def construct_from_heading(cls, point_on_line, heading):
        """construct_from_angle

        Given a point on the line and the angle of the line,
        determine the formula for the line and then use it
        to instantiate a Line.

        https://www.mathsisfun.com/geometry/unit-circle.html
        """

        instance = cls()

        polar_angle = compass_heading_to_polar_angle(heading)
        x_offset = cos(polar_angle)
        #
        # cos(pi/2) and cos(3pi/2) aren't calculated as zero, but should be.
        #
        if abs(x_offset) < 6e-16:
            x_offset = 0.0
        y_offset = sin(polar_angle)

        second_point = Point(point_on_line.x + x_offset,
                             point_on_line.y + y_offset)

        instance.slope, instance.y_intercept, instance.x = formula_from_points(
            point_on_line,
            second_point)

        return instance

    def find_intersection(self, line):
        """find_intersection

        Return the point where two lines intersect.
        """

        if self.slope == line.slope:
            #
            # They're parallel and therefore don't intersect.
            #
            return None

        if self.slope is INFINITE:
            intersection_x = self.x
            slope = line.slope
            y_intercept = line.y_intercept

        elif line.slope is INFINITE:
            intersection_x = line.x
            slope = self.slope
            y_intercept = self.y_intercept

        else:
            slope = line.slope
            y_intercept = line.y_intercept
            intersection_x = (float(self.y_intercept - line.y_intercept) /
                              (line.slope - self.slope))

        intersection_y = slope * intersection_x + y_intercept

        return Point(intersection_x, intersection_y)

    def find_perpendicular(self, point):
        """find_perpendicular

        Return a Line which passes through the point and is
        perpendicular to the current line.
        """

        p_x = None
        p_y_intercept = None
        if self.slope is INFINITE:
            p_slope = 0
            p_y_intercept = point.y
        elif self.slope == 0:
            p_slope = INFINITE
            if point.x == 0:
                #
                # TODO: This is questionable, since not everyone
                # agrees a vertical line (infinite slope) has
                # a Y intercept.
                #
                p_y_intercept = 0
            else:
                p_x = point.x
        else:
            p_slope = -1 * self.slope
            p_y_intercept = point.y - (p_slope * point.x)

        return Line.construct_from_formula(slope=p_slope, y_intercept=p_y_intercept, x=p_x)

    def on_the_line(self, point):
        """on_the_line Return True if point is on the line, otherwise False."""

        if self.slope is INFINITE:
            return self.x == point.x

        return point.y == self.slope * point.x + self.y_intercept

    def distance_to_point(self, point):
        """distance_to_point

        Calculate the shortest distance from point to the line.
        """

        if self.on_the_line(point):
            return 0

        #
        # 1. Find the perpendicular line
        # 2. Find the intersection of the two lines
        # 3. Calculate the distance between the point
        #    and the intersection
        #
        perpendicular = self.find_perpendicular(point)
        intersection = self.find_intersection(perpendicular)
        distance = points_distance(intersection, point)

        return distance

    def point_at_distance(self,
                          starting_point,
                          destination_point,
                          distance):
        """point_at_distance

        Find the point on the line which is distance units from
        the point on the line described by starting_point, in the
        direction of the point on the line described by
        destination_point. Return the found point.
        """
        #
        # We know the slope of the line (m or self.slope). We also know
        # the formula for a circle: (x - h)**2 + (y - k)**2 = r**2, where
        # (h, k) is the center of the circle and r is the radius.
        # If (h, k) is set to the starting_point, then the two x values
        # which are on the line AND distance (d) from the starting point
        # can be found with h +/- d / sqrt(1 + m**2). The correct x is the one
        # between the starting_point and the destination_point.
        #
        if self.slope is not INFINITE:
            first_x = starting_point.x + distance / sqrt(1 + self.slope**2)
            second_x = starting_point.x - distance / sqrt(1 + self.slope**2)
            #
            # Determine which x is in the appropriate direction and then
            # use the line's equation to determine the corresponding y.
            #
            if starting_point.x < destination_point.x:
                if first_x > starting_point.x:
                    x = first_x
                else:
                    x = second_x
            else:
                if first_x < starting_point.x:
                    x = first_x
                else:
                    x = second_x
            y = self.slope * x + self.y_intercept
        else:
            first_y = starting_point.y + distance
            second_y = starting_point.y - distance
            if starting_point.y < destination_point.y:
                if first_y > starting_point.y:
                    y = first_y
                else:
                    y = second_y
            else:
                if first_y < starting_point.y:
                    y = first_y
                else:
                    y = second_y
            x = starting_point.x

        return Point(x, y)

    def __repr__(self):
        """__repr__ Formatted output of the equation for the line."""

        if self.slope is INFINITE:
            return 'x = %f' % self.x

        if self.slope is 0:
            return 'y = %f' % self.y_intercept

        if self.y_intercept == 0:
            return 'y = %f * x' % (self.slope)
        elif self.y_intercept < 0:
            return 'y = %f * x - %f' % (self.slope, -1 * self.y_intercept)

        return 'y = %f * x + %f' % (self.slope, self.y_intercept)


class Polygon(object):
    """Polygon

    Representation of a polygon
    """

    def __init__(self, vertices):
        """__init__()

        Construct the representation of a polygon defined
        by the provided list of vertices.
        """

        if len(vertices) < 3:
            raise Exception("Must provide a minimum of three vertices")

        self._vertices = list()
        for vertex in vertices:
            self._vertices.append([vertex.x, vertex.y])

        self._vertex_path = mplPath.Path(self._vertices)

    def point_is_inside(self, point):
        """point_is_inside()

        https://stackoverflow.com/questions/16625507/python-checking-if-point-is-inside-a-polygon

        Return True if the given point is inside the polygon
        or on the edge, False otherwise.
        """

        return self._vertex_path.contains_point(point=point.as_tuple(),
                                                radius=-0.1)
