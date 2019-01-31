""" Auv

Exercise move_to_waypoint()
"""

import logging
from time import sleep, time

quitting_time = time() + 600.0

from auv_bonus_xprize.settings import config
from auv_bonus_xprize.auv_main_loop import limit_reached
from auv.auv import Auv

waypts = list()
# start        750214.5,1987358.1
waypts.append((750214.5,1987370.1, 4.0, 0)) # 12 m north
waypts.append((750189.5,1987370.1, 4.0, 0)) # 25 m west, 12 m north
waypts.append((750189.5,1987345.1, 4.0, 0)) # 25 m west, 13 m south
waypts.append((750214.5,1987345.1, 4.0, 0)) # 13 m south 
waypts.append((750214.5,1987358.1, 4.0, 0)) #

auv = Auv()
auv.strobe('OFF')
auv.watchdog.stop()

while not auv.auv_control.connected:
    print('Waiting to connect')
    sleep(1.0)

PAUSE = float(config['starting']['start_delay_secs'])
logging.debug('Pausing for {0} seconds'.format(PAUSE))

auv.watchdog.reset()
logging.debug('enable_steering()')
auv.enable_steering()
auv.plume_detected()
logging.debug('done enable_steering()')

for waypt in waypts:
    if limit_reached(auv):
        logging.warning('Time limit reached')
        break

    logging.debug('exercise_auv: moving to waypt {0}'.format(
        waypt))

    while auv.move_toward_waypoint(waypt) == 'MORE':
        if limit_reached(auv):
            break

        auv.watchdog.reset()
        auv.plume_detected()

        sleep(1.0)

auv.plume_detected()

logging.debug('surfacing')
auv.surface()
logging.debug('surfaced')
auv.plume_detected()

auv.auv_control.publish_variable(
    'DESIRED_SPEED',
    0.0,
    -1)
auv.strobe('ON')

logging.debug('Done')
