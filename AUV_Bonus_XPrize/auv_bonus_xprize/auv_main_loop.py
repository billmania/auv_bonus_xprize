"""The main loop for the AUV control system
"""

import logging
from time import time, sleep
from enum import Enum, unique
from auv_bonus_xprize.settings import config
from auv.auv import Auv
from searchspace.searchspace import SearchSpace


@unique
class AUVState(Enum):
    SearchForPlume = 1
    NewSearchArea = 2
    Done = 3
    RefreshPosition = 4
    ReportResults = 5
    AbortMission = 9


def search_for_plume(auv, search_space):
    """search_for_plume()

    Calculate a search path and then follow that search path
    until the end or the plume is found.
    """

    logging.debug('search_for_plume()')

    search_path = search_space.calculate_search_path()
    for waypt in search_path:
        set_loop_hz(float(config['DEFAULT']['main_loop_hz']))
        while auv.move_toward_waypoint(waypt) == 'MORE':
            watchdog()
            if auv.plume_detected():
                return AUVState.NewSearchArea
            loop_hz()

    return AUVState.ReportResults

def constrain_search_area(auv, search_space):
    """constrain_search_area()

    Further constrain the search area, so a new
    search path can be calculatd.
    """

    logging.debug('constrain_search_area()')
    return AUVState.SearchForPlume


def refresh_position(auv, search_space):
    """refresh_position()
    """

    logging.debug('refresh_position()')
    return AUVState.ReportResults


def report_results(auv, search_space):
    """report_results()
    """

    logging.debug('report_results()')
    return AUVState.Done


def abort_mission(auv, search_space):
    """abort_mission()
    """

    logging.debug('abort_mission()')
    return AUVState.Done


def watchdog():
    """watchdog()

    Reset the watchdog timer.
    """

    if hasattr(watchdog, 'reset_time'):
        elapsed_time = time() - watchdog.reset_time
    else:
        elapsed_time = 0.0

    logging.debug("Resetting the watchdog timer after {0}".format(
        elapsed_time) +
                  "seconds")

    if elapsed_time >= float(config['auv']['watchdog_timer']):
        # TODO send reset message
        watchdog.reset_time = time()


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
state_function[AUVState.SearchForPlume] = search_for_plume
state_function[AUVState.NewSearchArea] = constrain_search_area
state_function[AUVState.RefreshPosition] = refresh_position
state_function[AUVState.ReportResults] = report_results
state_function[AUVState.AbortMission] = abort_mission


def main_loop():
    """main_loop()

    The main logic loop for the AUV control system.
    """

    logging.debug('Instantiating the SearchSpace() object')
    watchdog()
    search_space = SearchSpace()
    search_space.set_search_boundaries()
    search_space.set_current_velocity()

    logging.debug('Instantiating the Auv() object')
    watchdog()
    auv = Auv()
    logging.debug('Waiting until the AUV is connected')
    while not auv.auv_control.connected:
        sleep(1.0)
    logging.debug('AUV is connected')

    system_state = AUVState.SearchForPlume

    logging.debug('Starting the state loop')
    watchdog()
    while system_state not in [AUVState.AbortMission,
                               AUVState.ReportResults]:

        if auv.data_not_updated():
            logging.error('Data from AUV not up to date')
            system_state = AUVState.AbortMission
        else:
            system_state = state_function[system_state](
                auv,
                search_space)

        watchdog()

    state_function[system_state](auv, search_space)

if __name__ == '__main__':
    logging.info('Starting AUV main loop, version {0}'.format(
        config['DEFAULT']['version']
    ))

    main_loop()

    logging.info('Finished AUV main loop')
