"""The main loop for the AUV control system
"""

import logging
from enum import Enum, unique
from auv_bonus_xprize.settings import config
from auv.auv import Auv
from searchspace.searchspace import SearchSpace


@unique
class AUVState(Enum):
    SearchForPlume = 1
    FollowPlume = 2
    ReacquirePlume = 3
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
        distance_to_waypt = auv.distance_to_waypt(waypt)
        depth_to_waypt = auv.depth_to_waypt(waypt)

        if (distance_to_waypt < float(config['auv']['distance_tolerance']) and
            depth_to_waypt > float(config['auv']['depth_tolerance'])):

            auv.move_to_depth(waypt)

        while distance_to_waypt > float(config['auv']['distance_tolerance']):
            auv.move_to_waypt(waypt)

    return AUVState.FollowPlume


def follow_plume(auv, search_space):
    """follow_plume()
    """

    logging.debug('follow_plume()')
    return AUVState.ReacquirePlume


def reacquire_plume(auv, search_space):
    """follow_plume()
    """

    logging.debug('reacquire_plume()')
    return AUVState.RefreshPosition


def refresh_position(auv, search_space):
    """refresh_position()
    """

    logging.debug('refresh_position()')
    return AUVState.ReportResults


def report_results(auv, search_space):
    """report_results()
    """

    logging.debug('report_results()')
    return AUVState.AbortMission


def abort_mission(auv, search_space):
    """abort_mission()
    """

    logging.debug('abort_mission()')
    return AUVState.AbortMission


state_function = dict()
state_function[AUVState.SearchForPlume] = search_for_plume
state_function[AUVState.FollowPlume] = follow_plume
state_function[AUVState.ReacquirePlume] = reacquire_plume
state_function[AUVState.RefreshPosition] = refresh_position
state_function[AUVState.ReportResults] = report_results
state_function[AUVState.AbortMission] = abort_mission


def main_loop():
    """main_loop()

    The main logic loop for the AUV control system.
    """

    logging.debug('Instantiating the Auv() object')
    auv = Auv()
    logging.debug('Instantiating the SearchSpace() object')

    search_space = SearchSpace(
        auv_latitude=float(config['starting']['latitude']),
        auv_longitude=float(config['starting']['longitude'])
    )
    search_space.set_search_boundaries(
        northern_latitude=float(config['starting']['northern_latitude']),
        southern_latitude=float(config['starting']['southern_latitude']),
        eastern_longitude=float(config['starting']['eastern_longitude']),
        western_longitude=float(config['starting']['western_longitude']))
    search_space.set_current_velocity(
        current_set=float(config['starting']['set']),
        current_drift=float(config['starting']['drift']))


    system_state = AUVState.SearchForPlume

    while system_state not in [AUVState.AbortMission,
                               AUVState.ReportResults]:

        system_state = state_function[system_state](
            auv,
            search_space)

    state_function[system_state](auv, search_space)

if __name__ == '__main__':
    logging.info('Starting AUV main loop, version {0}'.format(
        config['DEFAULT']['version']
    ))

    main_loop()

    logging.info('Finished AUV main loop')
