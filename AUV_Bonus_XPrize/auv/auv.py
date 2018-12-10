"""Auv

The functionality for the AUV.
"""

import logging
from math import sqrt
from auv_bonus_xprize.settings import config
from auv.auv_moos import AuvMOOS


class Auv(object):
    """Auv - The representation of the AUV.

DESIRED_ELEVATOR
DESIRED_RUDDER
DESIRED_THRUST
RT_RELEASE_DROPWEIGHT

    """
    def __init__(self, x=0.0, y=0.0, depth=0.0, heading=0.0):
        """__init__() - Create an instance of the AUV
        """

        self._current_pose = dict()
        self._current_pose['lat'] = x
        self._current_pose['lon'] = y
        self._current_pose['x'] = 0.0
        self._current_pose['y'] = 0.0
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

        variables_list = ['IMU_HEADING',
                          'PS_DEPTH',
                          'NAV_LAT',
                          'NAV_LONG',
                          'NAV_X',
                          'NAV_Y']
        self.auv_control = AuvMOOS(
            config['auv']['host'],
            int(config['auv']['port']),
            config['auv']['community'],
            variables_list)
        self.auv_control.set_data_callback(self._process_auv_data)

    def _process_auv_data(self, moos_variable_name, moos_variable_value):
        """_process_auv_data()

        The function called by the underlying MOOS system each time new data
        is received from the AUV.
        """

        logging.debug('_process_auv_data() called')

        if moos_variable_name == 'NAV_LAT':
            self._current_pose['lat'] = moos_variable_value
        elif moos_variable_name == 'NAV_LONG':
            self._current_pose['lon'] = moos_variable_value
        elif moos_variable_name == 'NAV_X':
            self._current_pose['x'] = moos_variable_value
        elif moos_variable_name == 'NAV_Y':
            self._current_pose['y'] = moos_variable_value
        elif moos_variable_name == 'PS_DEPTH':
            self._current_pose['depth'] = moos_variable_value
        elif moos_variable_name == 'IMU_HEADING':
            self._current_pose['heading'] = moos_variable_value

    def move_to_waypoint(self, waypoint):
        """move_to_waypoint()

        Set the prop_velocity, the elevator, and the rudder
        in order to move the AUV from its current position
        to the waypoint.
        """

        self._current_waypoint['x'] = waypoint[0]
        self._current_waypoint['y'] = waypoint[1]
        self._current_waypoint['depth'] = waypoint[2]

        distance_tolerance = float(config['auv']['distance_tolerance'])
        while self.distance_to_waypoint() > distance_tolerance:
            #
            # Get new prop, elevator, and rudder settings based
            # on the bearing and range to the waypoint.
            # Execute those settings in a loop while checking
            # and recording dye levels.

            pass

    def distance_to_waypoint(self):

        """distance_to_waypoint()

        Calculate the straight-line-distance between the AUV's
        current position and the given waypoint.
        """

        distance = float(0)
        for axis in ['lat', 'lon', 'depth']:
            difference = pow(self._current_pose[axis] -
                             self._current_waypoint[axis], 2)
            distance += difference

        return sqrt(difference)

    def record_pose_update(
        self,
        x,
        y,
        depth,
        heading
    ):
        """record_pose_update()

        Used as a callback to collect the navigation updates from
        the AUV navigation subsystem and update the AUV's current
        pose.
        """

        self._current_pose['lat'] = x
        self._current_pose['lon'] = y
        self._current_pose['depth'] = depth
        self._current_pose['heading'] = heading

    def settings_for_waypoint(self, waypoint):
        """settings_for_waypoint()

        Get the bearing and range to the given waypoint and
        then calculate the appropriate prop speed, elevator,
        and rudder settings to move the AUV toward that waypoint.
        """

        prop_speed = 0.0
        elevator = 0.0
        rudder = 0.0

        return prop_speed, elevator, rudder
