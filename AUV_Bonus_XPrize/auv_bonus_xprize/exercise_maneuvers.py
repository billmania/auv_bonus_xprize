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
""" Maneuvers

Test the methods:

    wait_to_start
    enable_steering
    plume_detected
    surface

"""

import logging
from time import sleep

from auv_bonus_xprize.settings import config
from auv.auv import Auv

auv = Auv()

while not auv.auv_control.connected:
    print('Waiting to connect')
    sleep(1.0)

logging.debug('wait_to_start() {0}'.format(
    config['starting']['auv_position_utm']))
while auv.wait_to_start():
    auv.plume_detected()
    sleep(10)

logging.debug('enable_steering()')
auv.enable_steering()

auv.plume_detected()

logging.debug('surface()')
auv.surface()

auv.plume_detected()

auv.auv_control.publish_variable(
    'DESIRED_SPEED',
    0.0,
    -1)

logging.debug('Done')
