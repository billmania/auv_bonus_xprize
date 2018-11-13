"""Auv

The functionality for the AUV.
"""

from math import sqrt, pow
from auv_bonus_xprize.settings import config


class Auv(object):
    """Auv - The representation of the AUV.

    """
    def __init__(self, x=0.0, y=0.0, depth=0.0, heading=0.0):
        """__init__() - Create an instance of the AUV
        """

        self._current_pose = dict()
        self._current_pose['x'] = x
        self._current_pose['y'] = y
        self._current_pose['depth'] = depth
        self._current_pose['heading'] = heading

        self._dye_sensor = dict()
        self._dye_sensor['value'] = 0
        self._dye_sensor['gain'] = 0

        self._current_waypoint = dict()
        self._current_waypoint['x'] = 0.0
        self._current_waypoint['y'] = 0.0
        self._current_waypoint['depth'] = 0.0

        self._elevator = 0.0
        self._rudder = 0.0

        self._prop_velocity = 0

    def move_to_waypoint(self,
                         waypoint_x,
                         waypoint_y,
                         waypoint_depth):
        """move_to_waypoint()

        Control the prop_velocity, the elevator, and the rudder
        in order to move the AUV from its current position
        to the waypoint.
        """

        self._current_waypoint['x'] = waypoint_x
        self._current_waypoint['y'] = waypoint_y
        self._current_waypoint['depth'] = waypoint_depth

        distance_tolerance = float(config['auv']['distance_tolerance'])
        while self.distance_to_waypoint() > distance_tolerance:
            pass

    def distance_to_waypoint(self):

        """distance_to_waypoint()

        Calculate the straight-line-distance between the AUV's
        current position and the given waypoint.
        """

        distance = float(0)
        for axis in ['x', 'y', 'depth']:
            difference = pow(self._current_pose[axis] -
                             self._current_waypoint[axis], 2)
            distance += difference

        return sqrt(difference)
