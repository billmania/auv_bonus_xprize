"""Auv

The functionality for the AUV.
"""

import logging
from math import sqrt
from time import time, sleep
from auv_bonus_xprize.settings import config
from auv.auv_moos import AuvMOOS
from searchspace.geometry import bearing_to_point, Point


def variables_list():
    """variables_list()

    Return a list of the MOOS variables specified
    in the configuration file.
    """

    variables = list()
    variables.append(config['variables']['easting_x'])
    variables.append(config['variables']['northing_y'])
    variables.append(config['variables']['depth'])
    variables.append(config['variables']['altitude'])
    variables.append(config['variables']['heading'])
    variables.append(config['variables']['speed'])

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

    def data_not_updated(self):
        """data_not_updated()

        Returns True if the data from MOOS is getting old, which
        implies there's a problem with communication.
        """

        return (time() - self._auv_data['DATA_TIMESTAMP']) > float(config['auv']['max_data_delay_secs'])

    def _process_auv_data(self, moos_variable_name, moos_variable_value):
        """_process_auv_data()

        The function called by the underlying MOOS system each
        time new data is received from the AUV.
        """

        self._auv_data[moos_variable_name] = moos_variable_value
        self._auv_data['DATA_TIMESTAMP'] = time()

    def wait_to_start(self):
        """wait_to_start()

        Measure the distance between the AUV and the
        starting point defined in the config file. Don't
        return until that distance is less than twice
        the distance tolerance.
        """

        starting_position = config['starting']['auv_position_utm'].split(',')
        self._current_waypoint['x'] = float(starting_position[0])
        self._current_waypoint['y'] = float(starting_position[1])
        self._current_waypoint['depth'] = 0.0

        distance_to_start = self.distance_to_waypoint()
        if distance_to_start > (2.0 * float(config['auv']['distance_tolerance'])):
            logging.debug('Distance to starting position {0}'.format(
                distance_to_start))

            sleep(60.0)

    def plume_detected(self):
        """plume_detected()

        Sample the dye sensor. If the measurement is above
        the noise level, record the measurement and return
        True. Otherwise return False.
        """

        logging.info('{0}:{1},{2},{3} A{4} H{5}'.format(
            time(),
            self._auv_data[config['variables']['easting_x']],
            self._auv_data[config['variables']['northing_y']],
            self._auv_data[config['variables']['depth']],
            self._auv_data[config['variables']['altitude']],
            self._auv_data[config['variables']['heading']]
            ))

        return False

    def altitude_safety(self):
        """altitude_safety()

        Calculate and return the quantity of meters to
        subtract from the desired depth, in order to maintain
        a minimum altitude above the sea bottom.
        """

        min_altitude = float(config['auv']['min_altitude_meters'])
        altitude = self._auv_data[config['variables']['altitude']]
        if altitude < min_altitude:
            return min_altitude - altitude

        return 0.0

    def surface(self):
        """surface()

        Move the AUV to the surface and stop the propeller.
        """

        heading = self._auv_data[config['variables']['heading']]
        turn_amount = int(config['auv']['spiral_amount'])

        surface_depth = float(config['auv']['surface_depth'])
        while self._auv_data[config['variables']['depth']] > surface_depth:
            self.auv_control.publish_variable(
                config['variables']['set_heading'],
                heading,
                -1)
            self.auv_control.publish_variable(
                config['variables']['set_depth'],
                surface_depth,
                -1)
            self.auv_control.publish_variable(
                config['variables']['set_speed'],
                float(config['auv']['surface_speed']),
                -1)

            heading = float((int(heading) + turn_amount) % 360)
            sleep(1.0)

    def strobe(self, state):
        """strobe()

        Turn the tail strobe light ON or OFF.
        """

        if state == "ON":
            self.auv_control.publish_variable(
                'RT_ENABLE_WHITE_STROBE',
                1,
                -1)
        else:
            self.auv_control.publish_variable(
                'RT_ENABLE_WHITE_STROBE',
                0,
                -1)

    def enable_steering(self):
        """enable_steering()

        Ensure the AUV is submerged sufficiently to enable
        steering, because the AUV doesn't steer well on the
        surface.
        """

        steerage_depth = float(config['auv']['min_steerage_depth_meters'])
        while self._auv_data[config['variables']['depth']] < steerage_depth:
            self.auv_control.publish_variable(
                config['variables']['set_heading'],
                self._auv_data[config['variables']['heading']],
                -1)
            self.auv_control.publish_variable(
                config['variables']['set_depth'],
                steerage_depth,
                -1)
            self.auv_control.publish_variable(
                config['variables']['set_speed'],
                float(config['auv']['max_speed']),
                -1)

            sleep(0.5)

        self.auv_control.publish_variable(
            config['variables']['set_speed'],
            float(config['auv']['min_speed']),
            -1)

    def move_toward_waypoint(self, waypoint):
        """move_toward_waypoint()

        Compare the current position of the AUV to the given
        waypoint. Calculate the distance and the bearing to
        the waypoint. If either is greater than the tolerance
        parameters, calculate the appropriate amounts to adjust
        the heading, depth, and speed of the AUV and effect
        those adjustments. Return 'MORE' to indicate the AUV
        is not yet close enough.

        Otherwise, if the AUV is within the tolerances for
        the waypoint, return 'DONE'.
        """

        self._current_waypoint['x'] = waypoint[0]
        self._current_waypoint['y'] = waypoint[1]
        self._current_waypoint['depth'] = waypoint[2]
        _ = int(waypoint[3])

        logging.info('{0}:{1},{2},{3} A{4} H{5}'.format(
                        time(),
                        self._auv_data[config['variables']['easting_x']],
                        self._auv_data[config['variables']['northing_y']],
                        self._auv_data[config['variables']['depth']],
                        self._auv_data[config['variables']['altitude']],
                        self._auv_data[config['variables']['heading']]
                        ))

        if self.distance_to_waypoint() > float(config['auv']['distance_tolerance']):
            logging.debug('Moving toward the waypoint')
            bearing = bearing_to_point(
                Point(self._auv_data[config['variables']['easting_x']],
                      self._auv_data[config['variables']['northing_y']]),
                Point(self._current_waypoint['x'],
                      self._current_waypoint['y']))
            self.auv_control.publish_variable(
                config['variables']['set_heading'],
                bearing,
                -1)
            self.auv_control.publish_variable(
                config['variables']['set_depth'],
                self._current_waypoint['depth'] - self.altitude_safety(),
                -1)
            self.auv_control.publish_variable(
                config['variables']['set_speed'],
                float(config['auv']['max_speed']),
                -1)

            return 'MORE'

        elif (abs((self._current_waypoint['depth'] - self.altitude_safety()) -
                    self._auv_data[config['variables']['depth']]) >
                float(config['auv']['depth_tolerance'])):
            logging.debug('Moving toward the depth')

            self.auv_control.publish_variable(
                config['variables']['set_depth'],
                self._current_waypoint['depth'] - self.altitude_safety(),
                -1)
            self.auv_control.publish_variable(
                config['variables']['set_speed'],
                float(config['auv']['depth_speed']),
                -1)

            return 'MORE'

        else:
            logging.debug('Reached the waypoint and depth')
            return 'DONE'

    def distance_to_waypoint(self):

        """distance_to_waypoint()

        Calculate the 2D-distance between the AUV's
        current position and the given waypoint.
        """

        x = config['variables']['easting_x']
        y = config['variables']['northing_y']

        sum_of_squares = pow(self._auv_data[x] - self._current_waypoint['x'], 2)
        sum_of_squares += pow(self._auv_data[y] - self._current_waypoint['y'], 2)

        return sqrt(sum_of_squares)
