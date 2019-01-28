""" Auv

Exercise move_to_waypoint()
"""

import logging
from time import sleep

from auv.auv import Auv

waypts = list()
# start        750214.5,1987358.1
waypts.append((750214.5,1987370.1, 4.0, 0)) # 12 m north
waypts.append((750189.5,1987370.1, 4.0, 0)) # 25 m west, 12 m north
waypts.append((750189.5,1987345.1, 4.0, 0)) # 25 m west, 13 m south
waypts.append((750214.5,1987345.1, 4.0, 0)) # 13 m south 
waypts.append((750214.5,1987358.1, 4.0, 0)) #

auv = Auv()
auv.watchdog.stop()

while not auv.auv_control.connected:
    print('Waiting to connect')
    sleep(1.0)

PAUSE = 120.0
logging.debug('Pausing for {0} seconds'.format(PAUSE))

auv.strobe('OFF')
sleep(PAUSE)
auv.strobe('ON')

auv.watchdog.reset()
logging.debug('enable_steering()')
auv.enable_steering()
auv.plume_detected()
logging.debug('done enable_steering()')

for waypt in waypts:
    logging.debug('exercise_auv: moving to waypt {0}'.format(
        waypt))

    iterations = 200
    while iterations and auv.move_toward_waypoint(waypt) == 'MORE':
        auv.watchdog.reset()
        auv.plume_detected()

        sleep(1.0)
        iterations = iterations - 1

    logging.debug('exercise_auv: remaining iterations {0}'.format(iterations))

auv.plume_detected()

logging.debug('surface()')
auv.surface()
auv.plume_detected()

auv.auv_control.publish_variable(
    'DESIRED_SPEED',
    0.0,
    -1)

logging.debug('Done')
