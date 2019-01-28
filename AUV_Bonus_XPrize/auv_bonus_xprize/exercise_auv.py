""" Auv

Exercise move_to_waypoint()
"""

import logging
from time import sleep

from auv.auv import Auv

#
# Centered around 17.9722238,-66.6206948
#                 751977.0,1988727.0
#
waypts = list()
waypts.append((751977.0, 1988732.0, 3.0, 0))
waypts.append((751967.0, 1988732.0, 3.0, 0))
waypts.append((751967.0, 1988722.0, 3.0, 0))
waypts.append((751977.0, 1988722.0, 3.0, 0))
waypts.append((751977.0, 1988727.0, 3.0, 0))

auv = Auv()
auv.watchdog.stop()

while not auv.auv_control.connected:
    print('Waiting to connect')
    sleep(1.0)

PAUSE = 120.0
logging.debug('Pausing for {0} seconds'.format(PAUSE))

sleep(PAUSE)
auv.strobe('ON')

auv.watchdog.reset()
logging.debug('enable_steering()')
auv.enable_steering()
logging.debug('done enable_steering()')

for waypt in waypts:
    logging.debug('moving to waypt {0}'.format(
        waypt))

    iterations = 200
    while iterations and auv.move_toward_waypoint(waypt) == 'MORE':
        auv.watchdog.reset()
        auv.plume_detected()

        sleep(1.0)
        iterations = iterations - 1

    logging.debug('remaining iterations {0}'.format(iterations))

auv.plume_detected()

logging.debug('surface()')
auv.surface()

auv.plume_detected()

auv.auv_control.publish_variable(
    'DESIRED_SPEED',
    0.0,
    -1)

logging.debug('Done')
