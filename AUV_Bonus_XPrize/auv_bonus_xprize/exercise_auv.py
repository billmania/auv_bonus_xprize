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

speed = 15.0
base_angle = 10.0

def wiggle_controls():

    print('Wiggling')
    for angle in [-(base_angle), 0.0, base_angle]:
        print('Elevator: {0}'.format(angle))
        auv.auv_control._publish_variable('DESIRED_ELEVATOR',
                                          angle,
                                          -1)
        sleep(1.0)
    for angle in [-(base_angle), 0.0, base_angle]:
        print('Rudder: {0}'.format(angle))
        auv.auv_control._publish_variable('DESIRED_RUDDER',
                                          angle,
                                          -1)
        sleep(1.0)

auv = Auv(x=float(config['starting']['latitude']),
          y=float(config['starting']['longitude']),
          depth=0.0,
          heading=int(config['starting']['heading']))

while not auv.auv_control.connected:
    print('Waiting to connect')
    sleep(1.0)

wiggle_controls()

print('Centering controls')
auv.auv_control._publish_variable('DESIRED_ELEVATOR',
                                  0.0,
                                  -1)
auv.auv_control._publish_variable('DESIRED_RUDDER',
                                  0.0,
                                  -1)

speed_increment = 0.0
while speed_increment <= speed:
    print('Setting speed to {0}'.format(speed_increment))
    auv.auv_control._publish_variable('DESIRED_THRUST',
                                      speed_increment,
                                      -1)
    sleep(0.2)
    speed_increment += 0.5

sleep(1.0)

print('Reversing')
auv.auv_control._publish_variable('DESIRED_THRUST',
                                  -(speed),
                                  -1)
sleep(0.2)
print('Stopped')
auv.auv_control._publish_variable('DESIRED_THRUST',
                                  0.0,
                                  -1)
print('Done')
