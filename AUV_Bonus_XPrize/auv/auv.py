"""Auv

The functionality for the AUV.
"""

import logging
from math import sqrt
from time import time, sleep
from auv_bonus_xprize.settings import config
from auv.auv_moos import AuvMOOS
from auv.watchdog import Watchdog
from auv.dye_sensor import DyeSensor
from searchspace.geometry import bearing_to_point, Point

STROBE = {
    "ON": 1,
    "OFF": 0
}


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

        self.watchdog = Watchdog()
        self.dye = DyeSensor()

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
        starting point defined in the config file. If
        the distance is less than twice the distance
        tolerance, return False.
        """

        starting_position = config['starting']['auv_position_utm'].split(',')
        self._current_waypoint['x'] = float(starting_position[0])
        self._current_waypoint['y'] = float(starting_position[1])
        self._current_waypoint['depth'] = 0.0

        distance_to_start = self.distance_to_waypoint()
        if distance_to_start > (2.0 * float(config['auv']['distance_tolerance'])):
            logging.debug('Distance to starting position {0}'.format(
                distance_to_start))

            return True

        return False

    def plume_detected(self):
        """plume_detected()

        Sample the dye sensor. If the measurement is above
        the noise level, record the measurement and return
        True. Otherwise return False.
        """

        sensor_value = self.dye.sensor_value()
        logging.info('DATA,{0},{1},{2},{3},{4},{5},{6}'.format(
            time(),
            self._auv_data[config['variables']['easting_x']],
            self._auv_data[config['variables']['northing_y']],
            self._auv_data[config['variables']['depth']],
            self._auv_data[config['variables']['altitude']],
            self._auv_data[config['variables']['heading']],
            sensor_value
            ))

        current_depth = self._auv_data[config['variables']['depth']]
        min_sensor_depth = float(config['dye_sensor']['min_sensor_depth'])
        if current_depth < min_sensor_depth:
            logging.debug('Too shallow for dye sensor')
            return False

        detection_threshold = int(config['dye_sensor']['plume_detected_value']);
        if sensor_value >= detection_threshold:
            logging.debug('Plume detected: {0}'.format(
                sensor_value))
            return True

        return False

    def altitude_safety(self):
        """altitude_safety()

        Calculate and return the quantity of meters to
        subtract from the desired depth, in order to maintain
        a minimum altitude above the sea bottom.
        """

        min_altitude = float(config['auv']['min_altitude_meters'])
        altitude = self._auv_data[config['variables']['altitude']]
        #
        # The altimeter reports 0.0 when it's out of range,
        # instead of something sensible like NA or the maximum
        # range.
        #
        if 0.0 < altitude < min_altitude:
            logging.debug('altitude_safety() Adjusting altitude')
            return min_altitude - altitude

        return 0.0

    def turn_toward_heading(
        self,
        heading: int,
        new_heading: int) -> int:
        """turn_toward_heading()

        Given a heading and a new heading calculate
        an intermediate heading which moves toward the
        new heading.
        """

        turn_increment = int(config['auv']['spiral_amount'])
        if new_heading < heading:
            if (heading - new_heading) < 180:
                turn_heading = heading - turn_increment
                if turn_heading < 0:
                    return turn_heading + 360
                return turn_heading
            else:
                return (heading + turn_increment) % 360
        else:
            if (new_heading - heading) < 180:
                return (heading + turn_increment) % 360
            else:
                turn_heading = heading - turn_increment
                if turn_heading < 0:
                    return turn_heading + 360
                return turn_heading

    def surface(self):
        """surface()

        Move the AUV to the surface and stop the propeller.
        """

        heading = self._auv_data[config['variables']['heading']]
        turn_amount = int(config['auv']['spiral_amount'])

        surface_depth = float(config['auv']['surface_depth'])
        while self._auv_data[config['variables']['depth']] > surface_depth:
            self.watchdog.reset()

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

        if state in STROBE:
            self.auv_control.publish_variable(
                'RT_ENABLE_WHITE_STROBE',
                STROBE[state],
                -1)

    def enable_steering(self):
        """enable_steering()

        Ensure the AUV is submerged sufficiently to enable
        steering, because the AUV doesn't steer well on the
        surface.
        """

        steerage_depth = float(config['auv']['min_steerage_depth_meters'])
        heading = self._auv_data[config['variables']['heading']]
        iterations = 100
        logging.debug('enable_steering(): iter {0}, head {1}, min depth {2}, dive speed {3}'.format(
            iterations,
            heading,
            config['variables']['set_depth'],
            config['auv']['steering_dive_speed']))

        while iterations and self._auv_data[config['variables']['depth']] < steerage_depth:
            iterations = iterations - 1
            self.auv_control.publish_variable(
                config['variables']['set_heading'],
                heading,
                -1)
            self.auv_control.publish_variable(
                config['variables']['set_depth'],
                steerage_depth,
                -1)
            self.auv_control.publish_variable(
                config['variables']['set_speed'],
                float(config['auv']['steering_dive_speed']),
                -1)

            sleep(0.5)

        logging.debug('enable_steering() ending iter {0}, depth {1}'.format(
            iterations,
            self._auv_data[config['variables']['depth']]))
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

        if self.distance_to_waypoint() > float(config['auv']['distance_tolerance']):
            logging.debug('move_toward_waypoint(): Moving toward the waypoint')
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
            logging.debug('move_toward_waypoint(): Moving toward the depth')

            heading = self.turn_toward_heading(
                    int(self._auv_data[config['variables']['heading']]),
                    int(config['starting']['set']))
            self.auv_control.publish_variable(
                config['variables']['set_heading'],
                heading,
                -1)
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
            logging.debug('move_toward_waypoint(): Reached the waypoint and depth')
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
