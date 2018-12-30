"""Auv

The functionality for the AUV.
"""

from math import sqrt
from auv_bonus_xprize.settings import config
from auv.auv_moos import AuvMOOS


def variables_list():
    """variables_list()

    Return a list of the MOOS variables specified
    in the configuration file.
    """

    variables = list()
    variables.append(config['variables']['easting_x'])
    variables.append(config['variables']['northing_y'])
    variables.append(config['variables']['depth'])
    variables.append(config['variables']['heading'])

    return variables


class Auv(object):
    """Auv - The representation of the AUV.

    """

    def __init__(self):
        """__init__() - Create an instance of the AUV
        """

        self._auv_data = dict()
        for variable_name in variables_list():
            self._auv_data[variable_name] = None

        self._current_waypoint = dict()
        self._current_waypoint['x'] = 0.0
        self._current_waypoint['y'] = 0.0
        self._current_waypoint['depth'] = 0.0

        self.auv_control = AuvMOOS(
            config['auv']['host'],
            int(config['auv']['port']),
            config['auv']['client_name'],
            variables_list())
        self.auv_control.set_data_callback(self._process_auv_data)

    def _process_auv_data(self, moos_variable_name, moos_variable_value):
        """_process_auv_data()

        The function called by the underlying MOOS system each time new data
        is received from the AUV.
        """

        self._auv_data[moos_variable_name] = moos_variable_value

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

        x = config['variables']['easting_x']
        y = config['variables']['northing_y']
        depth = config['variables']['depth']

        distance = float(0)
        distance = pow(self._auv_data[x] -
                       self._current_waypoint['x'], 2)
        distance += pow(self._auv_data[y] -
                        self._current_waypoint['y'], 2)
        distance += pow(self._auv_data[depth] -
                        self._current_waypoint['depth'], 2)

        return sqrt(distance)
