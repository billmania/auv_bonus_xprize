#
# Designed and written by:
# Bill Mania
# bill@manialabs.us
#
# under contract to:
# Valley Christian Schools
# San Jose, CA
#
# to compete in the:
# NOAA Bonus XPrize
# January 2019
#
"""The main loop for the AUV control system
"""

import logging
from math import cos, sin
from time import time, sleep
from enum import Enum, unique
from auv_bonus_xprize.settings import config
from auv.auv import Auv
from searchspace.searchspace import SearchSpace
from searchspace.geometry import compass_heading_to_polar_angle

quitting_time = time() + 10.0


@unique
class AUVState(Enum):
    SearchForPlume = 1
    ConstrainSearchArea = 2
    Done = 3
    ShiftSearchArea = 4
    ReportResults = 5
    WaitingToStart = 6
    AbortMission = 9


def limit_reached(auv):
    """limit_reached()

    Check all of the limits. If at least one has been reached,
    return True.
    """

#    logging.debug('data: {0}, voltage: {1}, min: {2}, quitting: {3}, time: {4}'.format(
#        auv.data_not_updated(),
#        auv._auv_data[config['variables']['battery']],
#        float(config['auv']['min_battery_voltage']),
#        quitting_time,
#        time()))

    if auv.data_not_updated():
        logging.error('Data from AUV not up to date')

    battery_voltage = float(auv._auv_data[config['variables']
                                                ['battery']])
    min_battery_voltage = float(config['auv']['min_battery_voltage'])
    if not battery_voltage or battery_voltage < min_battery_voltage:
        logging.error('min_battery_voltage threshold: {0}'.format(
            battery_voltage))
        return True

    if quitting_time and time() > quitting_time:
        logging.error('Time limit reached')
        return True

    return False


def waiting_to_start(auv, search_space):
    """waiting_to_start()

    Get the AUV starting position from the config file
    and then wait until the AUV is close to that position.
    """
    global quitting_time

    logging.debug('waiting_to_start()')
    auv.strobe('OFF')
    auv.watchdog.stop()

    set_loop_hz(1.0/60.0)
    while auv.wait_to_start():
        auv.plume_detected()
        loop_hz()

    logging.debug('At the starting location')

    auv.strobe('ON')
    sleep(3.0)
    auv.strobe('OFF')

    time_limit = float(config['search']['time_limit_secs'])
    quitting_time = time() + time_limit
    logging.debug('waiting_to_start(): time_limit is {0}, quitting_time is {1}'.format(
        time_limit,
        quitting_time))

    auv.watchdog.reset()
    logging.debug('waiting_to_start(): enable_steering()')
    auv.enable_steering()

    return AUVState.SearchForPlume


def search_for_plume(auv, search_space):
    """search_for_plume()

    Calculate a search path and then follow that search path
    until the end or the plume is found.
    """

    logging.debug('search_for_plume()')

    auv.watchdog.stop()
    search_path = search_space.calculate_search_path()
    auv.watchdog.reset()

    for waypt in search_path:
        logging.debug('search_for_plume(): Moving to waypt {0}'.format(waypt))
        set_loop_hz(float(config['DEFAULT']['main_loop_hz']))
        while auv.move_toward_waypoint(waypt) == 'MORE':
            auv.watchdog.reset()

            if limit_reached(auv):
                return AUVState.AbortMission

            if auv.plume_detected():
                current_depth = auv._auv_data[config['variables']['depth']]
                above_the_bottom = float(config['search']['max_depth']) - current_depth
                depth_tolerance = float(config['auv']['depth_tolerance'])
                if abs(above_the_bottom) <= depth_tolerance:
                    return AUVState.ReportResults
                else:
                    if search_for_plume.already_constrained:
                        return AUVState.ShiftSearchArea
                    else:
                        search_for_plume.already_constrained = True
                        return AUVState.ConstrainSearchArea

            loop_hz()

    return AUVState.ShiftSearchArea


def constrain_search_area(auv, search_space):
    """constrain_search_area()

    Further constrain the search area, so a new
    search path can be calculated based on a new
    position of the AUV which has been shifted up-current.
    """

    constrain_search_area.already_constrained = False

    logging.debug('constrain_search_area()')

    auv_x = auv._auv_data[config['variables']['easting_x']]
    auv_y = auv._auv_data[config['variables']['northing_y']]
    up_current_bearing = (int(config['starting']['set']) + 180) % 360
    up_current_offset = float(config['search']['up_current_offset'])
    angle_to_start = compass_heading_to_polar_angle(up_current_bearing)
    starting_x = round(cos(angle_to_start) * up_current_offset + auv_x, 1)
    starting_y = round(sin(angle_to_start) * up_current_offset + auv_y, 1)
    new_auv_position_utm = '{0},{1}'.format(starting_x, starting_y)
    config['starting']['auv_position_utm'] = new_auv_position_utm

    vertex_offset = float(config['search']['vertex_offset'])
    northern_y = round(starting_y + vertex_offset, 1)
    eastern_x = round(starting_x + vertex_offset, 1)
    southern_y = round(starting_y - vertex_offset, 1)
    western_x = round(starting_x - vertex_offset, 1)
    northwest_utm = '{0},{1}'.format(western_x, northern_y)
    northeast_utm = '{0},{1}'.format(eastern_x, northern_y)
    southeast_utm = '{0},{1}'.format(eastern_x, southern_y)
    southwest_utm = '{0},{1}'.format(western_x, southern_y)
    config['starting']['northwest_utm'] = northwest_utm
    config['starting']['northeast_utm'] = northeast_utm
    config['starting']['southeast_utm'] = southeast_utm
    config['starting']['southwest_utm'] = southwest_utm

    min_depth_offset = float(config['search']['min_depth_offset'])
    auv_depth = auv._auv_data[config['variables']['depth']]
    if (auv_depth - min_depth_offset) > float(config['search']['min_depth_meters']):
        config['search']['min_depth_meters'] = '{0}'.format(auv_depth - min_depth_offset)

    return AUVState.SearchForPlume


def shift_search_area(auv, search_space):
    """shift_search_area()

    Don't constrain the search area, only
    move the AUV's start position up-current.
    """

    logging.debug('shift_search_area()')

    auv_x = auv._auv_data[config['variables']['easting_x']]
    auv_y = auv._auv_data[config['variables']['northing_y']]
    up_current_bearing = (int(config['starting']['set']) + 180) % 360
    up_current_offset = float(config['search']['up_current_offset'])
    angle_to_start = compass_heading_to_polar_angle(up_current_bearing)
    starting_x = round(cos(angle_to_start) * up_current_offset + auv_x, 1)
    starting_y = round(sin(angle_to_start) * up_current_offset + auv_y, 1)
    new_auv_position_utm = '{0},{1}'.format(starting_x, starting_y)
    config['starting']['auv_position_utm'] = new_auv_position_utm
    logging.debug('shift_search_area(): New AUV start position: {0}'.format(
        config['starting']['auv_position_utm']))

    return AUVState.SearchForPlume


def report_results(auv, search_space):
    """report_results()
    """

    logging.debug('report_results()')

    auv.surface()
    auv.strobe('ON')
    auv.watchdog.send('Detected plume')

    return AUVState.Done


def abort_mission(auv, search_space):
    """abort_mission()
    """

    logging.debug('abort_mission()')

    auv.surface()
    logging.debug('abort_mission(): surface() completed')
    auv.strobe('ON')
    auv.watchdog.send('Aborted')

    return AUVState.Done


def set_loop_hz(desired_hz):
    """set_loop_hz()

    Set the period of a loop.
    """

    loop_hz.seconds_per_loop = 1.0 / desired_hz
    loop_hz.start_time = time()


def loop_hz():
    """loop_hz()

    Pause at the end of a loop to force the
    period of the loop.
    """

    pause = loop_hz.start_time + loop_hz.seconds_per_loop - time()
    if pause < 0:
        logging.warning('Loop frequency set too low')
    else:
        sleep(pause)

    loop_hz.start_time = time()


state_function = dict()
state_function[AUVState.WaitingToStart] = waiting_to_start
state_function[AUVState.SearchForPlume] = search_for_plume
state_function[AUVState.ConstrainSearchArea] = constrain_search_area
state_function[AUVState.ShiftSearchArea] = shift_search_area
state_function[AUVState.ReportResults] = report_results
state_function[AUVState.AbortMission] = abort_mission

search_for_plume.already_constrained = False


def main_loop():
    """main_loop()

    The main logic loop for the AUV control system.
    """

    logging.debug('Instantiating the SearchSpace() object')
    search_space = SearchSpace()
    search_space.set_search_boundaries()
    search_space.set_current_velocity()

    logging.debug('Instantiating the Auv() object')
    auv = Auv()
    auv.watchdog.reset()
    logging.debug('Waiting until the AUV is connected')
    while not auv.auv_control.connected:
        sleep(1.0)
    logging.debug('AUV is connected')

    system_state = AUVState.WaitingToStart

    logging.debug('Starting the state loop')
    auv.watchdog.reset()
    while system_state not in [AUVState.AbortMission,
                               AUVState.ReportResults]:

        if limit_reached(auv):
            system_state = AUVState.AbortMission
            break

        system_state = state_function[system_state](
            auv,
            search_space)

        auv.watchdog.reset()

    state_function[system_state](auv, search_space)

if __name__ == '__main__':
    logging.info('Starting AUV main loop, version {0}'.format(
        config['DEFAULT']['version']
    ))

    main_loop()

    logging.info('Finished AUV main loop')
