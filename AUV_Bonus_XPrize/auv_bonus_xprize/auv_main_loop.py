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
    ReportResults = 5
    WaitingToStart = 6
    AbortMission = 9


def waiting_to_start(auv, search_space):
    """waiting_to_start()

    Get the AUV starting position from the config file
    and then wait until the AUV is close to that position.
    """

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

    auv.watchdog.reset()

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
        set_loop_hz(float(config['DEFAULT']['main_loop_hz']))
        while auv.move_toward_waypoint(waypt) == 'MORE':
            auv.watchdog.reset()
            if auv.plume_detected():
                return AUVState.ReportResults
            loop_hz()

    return AUVState.AbortMission


def constrain_search_area(auv, search_space):
    """constrain_search_area()

    Further constrain the search area, so a new
    search path can be calculatd.
    """

    logging.debug('constrain_search_area()')
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
state_function[AUVState.NewSearchArea] = constrain_search_area
state_function[AUVState.ReportResults] = report_results
state_function[AUVState.AbortMission] = abort_mission


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

        if auv.data_not_updated():
            logging.error('Data from AUV not up to date')
            system_state = AUVState.AbortMission
        else:
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
