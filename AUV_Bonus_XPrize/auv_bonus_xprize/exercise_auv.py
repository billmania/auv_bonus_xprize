import logging
from time import sleep, time

from auv_bonus_xprize.settings import config
from auv.auv import Auv

"""
from RiptideMicroUUVInterface.cpp

"""

auv = Auv()

while not auv.auv_control.connected:
    print('Waiting to connect')
    sleep(1.0)


logging.info('{0}:{1},{2},{3} A{4} H{5}'.format(
    time(),
    auv._auv_data[config['variables']['easting_x']],
    auv._auv_data[config['variables']['northing_y']],
    auv._auv_data[config['variables']['depth']],
    auv._auv_data[config['variables']['altitude']],
    auv._auv_data[config['variables']['heading']]
    ))

logging.debug('enable_steering()')
auv.enable_steering()
logging.debug('at steering depth')

logging.info('{0}:{1},{2},{3} A{4} H{5}'.format(
    time(),
    auv._auv_data[config['variables']['easting_x']],
    auv._auv_data[config['variables']['northing_y']],
    auv._auv_data[config['variables']['depth']],
    auv._auv_data[config['variables']['altitude']],
    auv._auv_data[config['variables']['heading']]
    ))

waypt = (603931.0, 4126129.0, 1.0, 0)
logging.debug('moving to waypt {0}'.format(
    waypt))

iterations = 40
while iterations and auv.move_toward_waypoint(waypt) == 'MORE':
    logging.info('{0}:{1},{2},{3} A{4} H{5}'.format(
        time(),
        auv._auv_data[config['variables']['easting_x']],
        auv._auv_data[config['variables']['northing_y']],
        auv._auv_data[config['variables']['depth']],
        auv._auv_data[config['variables']['altitude']],
        auv._auv_data[config['variables']['heading']]
        ))
    sleep(1.0)
    iterations = iterations - 1

logging.debug('remainging iterations {0}'.format(iterations))

logging.debug('surfacing')
auv.surface()
logging.debug('done surfacing')

logging.info('{0}:{1},{2},{3} A{4} H{5}'.format(
    time(),
    auv._auv_data[config['variables']['easting_x']],
    auv._auv_data[config['variables']['northing_y']],
    auv._auv_data[config['variables']['depth']],
    auv._auv_data[config['variables']['altitude']],
    auv._auv_data[config['variables']['heading']]
    ))

auv.auv_control.publish_variable(
    'DESIRED_SPEED',
    0.0,
    -1)

logging.debug('Done')
