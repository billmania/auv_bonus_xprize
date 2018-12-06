"""The main loop for the AUV control system
"""

import logging
from enum import Enum, unique
from time import sleep
from auv_bonus_xprize.settings import config
from auv.auv import Auv
from searchspace.searchspace import SearchSpace


@unique
class AUVState(Enum):
    SearchForPlume = 1
    FollowPlume = 2
    ReacquirePlume = 3
    AbortMission = 9


def search_for_plume(auv, search_space):
    """search_for_plume()
    """

    logging.debug('search_for_plume()')
    new_state = AUVState.FollowPlume

    return new_state


def follow_plume(auv, search_space):
    """follow_plume()
    """

    logging.debug('follow_plume()')
    new_state = AUVState.ReacquirePlume

    return new_state


def reacquire_plume(auv, search_space):
    """follow_plume()
    """

    logging.debug('reacquire_plume()')
    new_state = AUVState.AbortMission

    return new_state


def abort_mission(auv, search_space):
    """abort_mission()
    """

    logging.debug('abort_mission()')
    new_state = AUVState.AbortMission

    return new_state

state_function = dict()
state_function[AUVState.SearchForPlume] = search_for_plume
state_function[AUVState.FollowPlume] = follow_plume
state_function[AUVState.ReacquirePlume] = reacquire_plume
state_function[AUVState.AbortMission] = abort_mission


def main_loop():
    """main_loop()

    The main logic loop for the AUV control system.
    """

#    logging.debug('Instantiating the Auv() object')
#    auv = Auv()
    auv = None
    logging.debug('Instantiating the SearchSpace() object')
    search_space = SearchSpace(auv_latitude=0.0,
                               auv_longitude=0.0)

    current_state = AUVState.SearchForPlume

    while current_state != AUVState.AbortMission:

        current_state = state_function[current_state](
            auv,
            search_space)

        sleep(5.0)


    state_function[current_state](auv, search_space)

if __name__ == '__main__':
    logging.info('Starting AUV main loop, version {0}'.format(
        config['DEFAULT']['version']
    ))

    main_loop()

    logging.info('Finished AUV main loop')
