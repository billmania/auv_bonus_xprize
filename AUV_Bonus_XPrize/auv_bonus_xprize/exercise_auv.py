from time import sleep

from auv_bonus_xprize.settings import config
from auv.auv import Auv

"""
DESIRED_RUDDER
DESIRED_DEPTH
DESIRED_HEADING
DESIRED_SPEED
DESIRED_THRUST
"""

speed = 50.0
base_angle = 10.0

def wiggle_controls():

while angle in [-(base_angle), 0.0, base_angle]:
    auv.auv_control._publish_variable('DESIRED_ELEVATOR',
                                      angle,
                                      -1)
    auv.auv_control._publish_variable('DESIRED_RUDDER',
                                      angle,
                                      -1)
    sleep(3.0)

auv = Auv(x=float(config['starting']['latitude']),
          y=float(config['starting']['longitude']),
          depth=0.0,
          heading=int(config['starting']['heading']))

wiggle_controls()

auv.auv_control._publish_variable('DESIRED_ELEVATOR',
                                  0.0,
                                  -1)
auv.auv_control._publish_variable('DESIRED_RUDDER',
                                  0.0,
                                  -1)
auv.auv_control._publish_variable('DESIRED_SPEED',
                                  speed,
                                  -1)

sleep(1.0)

auv.auv_control._publish_variable('DESIRED_SPEED',
                                  -(speed),
                                  -1)
sleep(0.2)
auv.auv_control._publish_variable('DESIRED_SPEED',
                                  0.0,
                                  -1)
